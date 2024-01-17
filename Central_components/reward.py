# the maximum acceptabel response time RTmax
import math
Rtmax = 100
import csv
#the reward of the response time
def RewardQos(rt,rtMax):
    if rt <= rtMax:
        return 1
    else:
        return math.exp(-((rt-Rtmax)/rtMax)**10)

def RewardUtility(Umaxs, Us):
    return sum(math.abs(Umaxs-Us))/len(Us) + 1

def Reward(RewardQos,RewardUtility):
    return RewardQos/RewardUtility

text = [i for i in range (0, 2100, 100)]
print(text)
with open('dummy_request.csv','w') as file:
    writer = csv.writer(file, delimiter=',')
    for word in text:
        writer.writerow([word])