import pandas as pd
def get_qos(path):
    #path = "~/haoyu/loadtest_test_stats.csv"
    df = pd.read_csv(path)
    return (df.iloc[-1])