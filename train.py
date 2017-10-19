""" This is an entry point for training of the model. """


from model.basic_model import BasicModel
from processing.dataset import Dataset


def main():
    roll_out = 20
    batch_size = 100
    dataset = Dataset("data/dataset/tunes.csv", {"tune_types": ["reel"]},
                      batch_size, roll_out, [0.7, 0.2, 0.1])
    dataset.save_encoding("data/logs/test_run_8")
    build_params = {"charset_size": dataset.get_charset_size(),
                    "roll_out": roll_out, "layers_count": 3,
                    "layers_size": 256}
    model = BasicModel(
        build_params, "data/logs/test_run_8/train",
        "data/logs/test_run_8/validation", "data/logs/test_run_8/checkpoints",
        "data/logs/test_run_8/best_model"
    )
    model.train(dataset, batch_size=batch_size, lstm_dropout=0.5,
                early_stopping=True)


if __name__ == "__main__":
    main()
