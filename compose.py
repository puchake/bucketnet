""" Entry point for model infering. """


from model.composer import Composer


def main():
    composer = Composer("data/logs/test_run_8/best_model/model",
                        "data/logs/test_run_8/best_model/model.meta",
                        "data/logs/test_run_8/encoder.dict",
                        "data/logs/test_run_8/decoder.dict")
    print(composer.compose("(3efd (3cdB A2 a2|(3aba (3gfe (3dAF (3DFA|GFED CEAG|\n", 300))


if __name__ == "__main__":
    main()
