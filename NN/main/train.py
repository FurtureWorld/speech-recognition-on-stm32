import importlib
import os
import NN.model
import NN.utility

from keras.models import load_model
from keras.callbacks import ReduceLROnPlateau

def train(data_set = None,data_per_batch=32,epoch=1,model_path='model.h5'):

    Dataset = None

    if data_set == None:
        dataloaders = os.listdir('Dataset')
        for dataloader in dataloaders:
            loader_path = os.path.join('Dataset',dataloader)
            if dataloader.endswith('.py') and os.path.isfile(loader_path) and dataloader!='__init__.py':
                try:
                    Dataset = importlib.import_module("Dataset." + dataloader[:-3])
                except Exception as ex:
                    print('failed to load Dataset from "%s".' % dataloader,ex)
                else:
                    print('successfuly loaded Dataset from "%s"!' % dataloader)
                    break
        if Dataset == None:
            raise Exception('No vaild dataset found!')
    else:
        try:
            Dataset = importlib.import_module("Dataset." + data_set)
        except Exception as ex:
            raise Exception('"%s" is not a vaild dataset!' % data_set)

    data_loader = Dataset.DataLoader(1024,data_per_batch,13)
    
    # 加载网络模型
    model = NN.model.create_model()
    # 输出网络结构
    model.summary()
    # 加载之前训练的数据
    if(os.path.exists(model_path)):
        model.load_weights(model_path)

    # 日志记录器
    csv_logger = NN.utility.LossHistory('training_log.csv')
    # 数据随机器
    radomizer = NN.utility.DataRadomizer(data_loader)
    # 防止手贱
    life_saver = NN.utility.ModelSaver(model,model_path,save_when_batch_end=True)
    # 自动降低lr
    reduce_lr = ReduceLROnPlateau('loss',verbose=1)
    # 开始训练
    res = model.fit_generator(
        data_loader.get_train_generator(),
        steps_per_epoch=1500,
        epochs=epoch,
        validation_data=data_loader.get_validation_generator(),
        validation_steps=32,
        callbacks=[csv_logger,radomizer,life_saver,reduce_lr])

    model.save_weights(model_path)
