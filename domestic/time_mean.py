
class time_mean:
    def __init__(self,num):
        self.__datas = [0 for i in range(num)]
        self.mean = 0
        self.__num = num
        self.__point = 0
        self.__cnt = 0
        self.enough = False
    
    def push(self,data):
        if self.__cnt < 5:
            self.__cnt += 1
            if self.__cnt == 5:
                self.enough = True
        self.mean *= self.__num
        self.mean -= self.__datas[self._point] - data
        self.__datas[self.__point] = data
        self.mean /= self.__num
