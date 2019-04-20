from copy import copy, deepcopy

from matplotlib import pyplot
import datetime
import numpy


class XuModelRecord:

    def __init__(self, t, Ab, As, P, previous=None):
        super().__init__()
        self.P = P
        self.Ab = Ab
        self.As = As
        self.t = t
        self.previous = previous


    @property
    def dAb(self):
        return ((self.Ab - self.previous.Ab) if self.previous else 0) / self.dt

    @property
    def dAs(self):
        return ((self.As - self.previous.As) if self.previous else 0) / self.dt

    @property
    def A(self):
        return self.Ab - self.As

    @property
    def dA(self):
        return ((self.A - self.previous.A) if self.previous else 0) / self.dt

    @property
    def dP(self):
        return ((self.P - self.previous.P) if self.previous else 0) / self.dt

    @property
    def dt(self):
        if self.previous:
            return (self.t - self.previous.t) / datetime.timedelta(minutes=1)
        return 1


class AgahXuModelRecord(XuModelRecord):

    def __init__(self, data, previous=None):
        super().__init__(
            P=data['FinalPrice'],
            As=data['BestAskQuantity'],
            Ab=data['BestBidQuantity'],
            t=eval(data['Time']),
            previous=previous
        )


# noinspection PyPep8Naming
class XuModel:
    def __init__(self, xu_records, blur_size=21):
        super().__init__()
        self.xu_records = deepcopy(list(xu_records))
        Ab = XuModel.mean(blur_size, [record.Ab for record in self.xu_records])
        As = XuModel.mean(blur_size, [record.As for record in self.xu_records])
        # base_price = self.xu_records[0].P
        for i, record in enumerate(self.xu_records):
            record.As = As[i]
            record.Ab = Ab[i]
            # record.P /= base_price
        self.k, self.b1, self.b2, self.b3, self.b4, self.s1, self.s2 = self.learn()

    @property
    def normal_time_delta(self):
        return (self.xu_records[-1].t - self.xu_records[0].t) / len(self.xu_records)

    def learn(self):
        # learn parameters in equation 3
        b = numpy.array([record.dP for record in self.xu_records])
        a = numpy.array([
            [record.A] for record in self.xu_records
        ])
        k = (numpy.linalg.lstsq(a, b))[0][0]

        # learn parameters in equations 5 and 6
        b_list = [record.dAb for record in self.xu_records]
        b_list.extend([record.dAs for record in self.xu_records])
        b = numpy.array(b_list)
        a_list = [
            [1 / record.P, -record.dP, record.Ab, -record.As, 0, 0] for record in self.xu_records
        ]
        a_list.extend([
            [0, 0, record.As, -record.Ab, record.P, record.dP] for record in self.xu_records
        ])
        a = numpy.array(a_list)
        b1, b2, b3, b4, s1, s2 = (numpy.linalg.lstsq(a, b))[0]

        return k, b1, b2, b3, b4, s1, s2

    def predict_next(self):
        last_record = self.xu_records[-1]
        lastT, lastP, lastAs, lastAb = last_record.t, last_record.P, last_record.As, last_record.Ab

        # the equations used here are kept from hand solving
        x = self.k * self.s2 * lastP - self.b4 * lastP - lastAs * self.k
        y = self.k * (self.b4 + self.b3 - 1)
        z = self.k * (self.s1 + self.s2) - self.b4
        xPrime = (self.b3 - 1) * lastP - self.k * lastAb + self.k * self.b2 * lastP
        yPrime = - (self.b3 - 1 + self.k * self.b2)
        zPrime = self.k * self.b1
        P = numpy.roots([
            self.k * z + y * yPrime,
            - (self.k * x + y * xPrime),
            y * zPrime
        ])

        if len(P) <= 0:
            raise Exception("Can't go further with this model. No answer found for P.")

        P = P[numpy.argmin(numpy.abs(P - lastP))]

        As = (x - z * P) / y
        Ab = (self.k * As + P - lastP) / self.k

        return XuModelRecord(
            lastT + self.normal_time_delta,
            Ab,
            As,
            P,
            last_record
        )

    def draw(self, deviation_time=None, prediction_time=None):
        t = [record.t for record in self.xu_records]
        Ab = [record.Ab for record in self.xu_records]
        As = [record.As for record in self.xu_records]
        P = [record.P for record in self.xu_records]
        prediction_model = None
        if deviation_time is not None:
            prediction_model = XuModel(
                xu_records=filter(lambda record: record.t < self.xu_records[0].t + deviation_time, self.xu_records),
                blur_size=1
            )
            while len(prediction_model.xu_records) < len(self.xu_records):
                prediction_model.predict_next_and_extend()
                if prediction_model.xu_records[-1].t > prediction_time + deviation_time + self.xu_records[0].t:
                    break
            predicted_t_axis = [record.t for record in prediction_model.xu_records]
        pyplot.subplot(311)
        pyplot.plot(t, P)
        pyplot.title('P')
        if deviation_time is not None:
            pyplot.plot(predicted_t_axis, [record.P for record in prediction_model.xu_records])
            pyplot.title('P\'')
        pyplot.subplot(312)
        pyplot.plot(t, Ab)
        pyplot.title('Ab')
        if deviation_time is not None:
            pyplot.plot(predicted_t_axis, [record.Ab for record in prediction_model.xu_records])
            pyplot.title('Ab\'')
        pyplot.subplot(313)
        pyplot.plot(t, As)
        pyplot.title('As')
        if deviation_time is not None:
            pyplot.plot(predicted_t_axis, [record.As for record in prediction_model.xu_records])
            pyplot.title('As\'')
        pyplot.tight_layout()
        pyplot.show()

    @staticmethod
    def mean(kernel_size, data: list):
        padding = numpy.ones((int(kernel_size / 2), ))
        inner_data = list(padding * data[0])
        inner_data.extend(data)
        inner_data.extend(padding * data[-1])
        result = []
        for i in range(len(data)):
            result.append(
                numpy.mean(inner_data[i: i + kernel_size])
            )
        return result

    def predict_next_and_extend(self):
        self.xu_records.append(self.predict_next())


map(print, [1]).__reduce__()