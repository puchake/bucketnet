""" Entry point for model infering. """


from model.composer import Composer


def main():
    composer = Composer("data/best_model/model", "data/best_model/model.meta",
                        "data/best_model/encoder.dict",
                        "data/best_model/decoder.dict")
    print(
        composer.compose(
            "\"Em\" e>d c<B \"D\" A2 GA |! \"G\" B3c \"D\" A3B | \"G\" G>B d<B \"C\" c2 (3ABc |\n", 300
        )
    )


if __name__ == "__main__":
    main()
