import numpy as np
from sklearn.model_selection import KFold
import matplotlib.pyplot as plt
from keras.callbacks import EarlyStopping


def slice_records(records, pred_len, post_len, increment=360*60, check_pred=True):
    for record in records:
        for start in range(0, len(record[0]) - pred_len - post_len, increment):
            pred_end = start + pred_len
            post_end = pred_end + post_len

            pred = record[0][start:pred_end]
            post = record[0][pred_end:post_end]

            pred_inds = np.logical_and(start <= record[1], record[1] < pred_end)
            post_inds = np.logical_and(pred_end <= record[1], record[1] < post_end)
            if check_pred:
                pred_labels = record[2][pred_inds]
                if np.all(pred_labels == 'N'):
                    pred_result = pred, record[1][pred_inds], pred_labels
                    post_result = post, record[1][post_inds], record[2][post_inds]
                    yield pred_result, post_result
            else:
                pred_result = pred, record[1][pred_inds], record[2][pred_inds]
                post_result = post, record[1][post_inds], record[2][post_inds]
                yield pred_result, post_result


def normalize_mean_std(values):
    mean = np.mean(values, axis=1)
    std = np.std(values, axis=1)
    return ((values.T - mean) / std).T


class ModelTester:
    def __init__(self, input_data, targets, folds=5, verbose=0):
        self.input_data = input_data
        self.targets = targets
        self.callbacks = [EarlyStopping(monitor='val_loss', patience=3)]
        self.verbose = verbose
        self.folds = folds

    def print_metrics(self, names, values):
        pairs = zip(names, values)
        strings = ['{}: {:.4f}'.format(name, val) for name, val in pairs]
        print(', '.join(strings))

    def print_final(self, names, values):
        mean = np.mean(values, axis=0)
        std = np.std(values, axis=0)
        triples = zip(names, mean, std)
        strings = ['{}: {:.4f} (+/-{:.4f})'.format(name, mean, std) for name, mean, std in triples]
        print(', '.join(strings))

    def plot_history(self, history):
        # plot history for loss
        w_val_loss = 'val_loss' in history.history
        plt.plot(history.history['loss'])
        if w_val_loss:
            plt.plot(history.history['val_loss'])
        plt.ylabel('loss')
        plt.xlabel('epoch')
        plt.legend(['train', 'test'], loc='upper left')
        plt.show()
        # plot history for accuracy
        plt.plot(history.history['binary_accuracy'])
        plt.plot(history.history['val_binary_accuracy'])
        plt.ylabel('accuracy')
        plt.xlabel('epoch')
        plt.legend(['train', 'test'], loc='upper left')
        plt.show()



    def test_model_crossv(self, model_builder, max_epochs, splitter):
        pass

    def test_model(self, model_builder, max_epochs=100):
        kfold_seed = 5

        kfold = KFold(n_splits=self.folds, shuffle=True, random_state=kfold_seed)

        cvscores = []
        best_model = None
        bests_history = None
        best_acc = None
        for train, test in kfold.split(self.input_data, self.targets):
            # Build model
            model = model_builder()
            # Fit the model
            history = model.fit(self.input_data[train],
                                self.targets[train],
                                epochs=max_epochs,
                                callbacks=self.callbacks,
                                validation_data=(self.input_data[test], self.targets[test]),
                                batch_size=32,
                                verbose=self.verbose)
            print("Trained for {} epochs".format(len(history.epoch)))
            # Evaluate the model
            scores = model.evaluate(self.input_data[test], self.targets[test], verbose=0)
            self.print_metrics(model.metrics_names, scores)
            cvscores.append(scores)
            if not best_acc or scores[1] > best_acc:
                best_acc = scores[1]
                best_model = model
                bests_history = history

        self.print_final(best_model.metrics_names, cvscores)
        self.plot_history(bests_history)
        return best_model
