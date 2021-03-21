import json

import bs4
import falcon
import requests

import models


class Client(object):
    
    auth = {
        'exempt_methods': ['POST']
    }

    def on_get(self, req, resp):
        pass

    def on_post(self, req, resp):
        data = req.media
        db_session = req.context['db_session']
        client = models.Client(**data)
        db_session.add(client)
        db_session.flush()
        for cur_name in {'USD', 'RUB'}:
            cur = db_session.query(models.Currency).filter_by(name=cur_name).one()
            acc = models.TransactionAccount(client_id=client.id, currency_id=cur.id, balance=0)
            client.transaction_accounts.append(acc)
        db_session.commit()
        resp_payload = {'created': {'client_account': str(client),
                         'transaction_accounts': [str(acc) for acc in client.transaction_accounts]}
                        }
        resp.body = json.dumps(resp_payload)


class Transaction(object):

    COMMISSION = 0.01
    MINIMAL_COMMISSIONS = {'USD': 10, 'RUB': 1000}
    REFERENCE_CURRENCY = 'RUB'
    DEFAULT_BONUS = 0

    def on_get(self, req, resp):
        pass

    def on_post(self, req, resp):
        data = req.media
        db_session = req.context['db_session']
        src_id = data.get('source')
        dst_id = data.get('destination')
        src = db_session.query(models.TransactionAccount).filter_by(id=src_id).one()
        if not self._is_owner(src, req.context['user']):
            resp.status = falcon.HTTP_401
            return
        dst = db_session.query(models.TransactionAccount).filter_by(id=dst_id).one()
        amount = int(data['amount'])
        commission = self._calc_commission(src, dst, amount)
        amount_to_pull = amount + commission
        src.balance -= amount_to_pull
        amount_to_put = self._calc_amount_to_put(src, dst, amount)
        dst.balance += amount_to_put

        th = models.TransactionHistory(sourse=src_id, destination=dst_id, amount=amount,
                                       commission=commission, bonus=self.DEFAULT_BONUS)
        db_session.add(th)                                       
        db_session.commit()
        
    @staticmethod
    def _is_owner(transaction_acc, creds):
        if (transaction_acc.client.username == creds['username']
                and transaction_acc.client.password == creds['password']):
            return True
        return False

    def _calc_commission(self, src, dst, amount):
        if src.client_id == dst.client_id:
            return 0
        commission = int(amount * self.COMMISSION)
        if commission < self.MINIMAL_COMMISSIONS[src.currency.name]:
            commission = self.MINIMAL_COMMISSIONS[src.currency.name]
        return commission

    def _calc_amount_to_put(self, src, dst, amount):
        if src.currency == dst.currency:
            return amount
        for cur in {src.currency, dst.currency}:
            if cur.name != self.REFERENCE_CURRENCY:
                foreign_cur = cur.name
                break
        exchange_rate = self._get_exchange_rate(foreign_cur)
        if src.currency.name == self.REFERENCE_CURRENCY:
            result = int(amount / exchange_rate)
        else:
            result = int(amount * exchange_rate)
        return result

    def _get_exchange_rate(self, currency):
        resp = requests.get('http://www.cbr.ru/scripts/XML_daily.asp')
        tree = bs4.BeautifulSoup(resp.content)
        for cur in tree.find_all('charcode'):
            if cur.text == currency:
                exchange_rate = cur.parent.select_one('value').text
                return float(exchange_rate.replace(',', '.'))
