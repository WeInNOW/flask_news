import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import linear_model
from sklearn.model_selection import train_test_split


def find_average_error(y_pred, y):
    # absolute = np.square((y_pred+1)/(y+1) - 1) # y 为 0 的情况
    # error = np.sum(absolute)
    # average_error = (error * 1.0) / len(absolute)

    average_error = np.sqrt(np.sum((y_pred - y) ** 2)/len(y)) # RMSE
    return average_error


titles = 'MVLR'
def MVLR(train_filename, test_filename, M):
    M_values = [1]
    train_errors = []
    test_errors = []

    dataTrain = pd.read_csv(train_filename)
    dataTest = pd.read_csv(test_filename)

    # '1spliter','2spliter', '3spliter', '4spliter', '5spliter', '6spliter',
    x_train = dataTrain[['1spliter','2spliter', '3spliter', '4spliter', '5spliter', '6spliter']]
    y_train = dataTrain['13spliter']

    #x_train, x_test, y_train, y_test = train_test_split(x_train, y_train, test_size=0.3, random_state=0)

    x_test = dataTest[['1spliter','2spliter', '3spliter', '4spliter', '5spliter', '6spliter']]
    y_test = dataTest['13spliter']

    ols = linear_model.LinearRegression()
    model = ols.fit(x_train, y_train) # 已自动训练。

    y_train_pred = model.predict(x_train)
    train_errors.append(find_average_error(y_train_pred, y_train))

    y_test_pred = model.predict(x_test)
    test_errors.append(find_average_error(y_test_pred, y_test))

    for i in range(2, M + 1):
        M_values.append(i)
        #x_train1 =
        #x_test1 = dataTrain[['1spliter','2spliter', '3spliter', '4spliter', '5spliter', '6spliter','7spliter','8spliter','9spliter','10spliter']]**i
        x_train1 = x_train ** i
        x_test1 = x_test ** i

        x_train_n = np.column_stack([x_train, x_train1])
        x_test_n = np.column_stack([x_test, x_test1])

        model = ols.fit(x_train_n, y_train)

        y_train_pred = model.predict(x_train_n)
        train_errors.append(find_average_error(y_train_pred, y_train))

        y_test_pred = model.predict(x_test_n)

        average_error = find_average_error(y_test_pred, y_test)
        print(average_error)
        test_errors.append(average_error)
    '''
    画图用，
    '''
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot([i for i in range(len(y_test))],y_test_pred, 'r', label='Prediction')
    ax.scatter([i for i in range(len(y_test))],y_test, label='Traning Data')
    ax.legend(loc=2)
    plt.show()
    print(y_test_pred)
    return M_values, train_errors, test_errors


def plot(M_values, train_errors, title):
    plt.plot(M_values, train_errors, label='train_error')
    plt.plot(M_values, test_errors, label='test_error')
    plt.xlabel("M")
    plt.ylabel("Average Error")
    plt.legend(loc='best')
    plt.title(title)
    plt.savefig('Average_error_vs_M.png')
    plt.show()
    plt.close()
    return 0


# Main function
train_filename = '30min_seven_train.csv'
test_filename = '30min_seven_test.csv'
M = 4
M_values, train_errors, test_errors = MVLR(train_filename, test_filename, M)
print(M_values)
print(train_errors)
print(test_errors)

title = titles
#plot(M_values, train_errors, title)