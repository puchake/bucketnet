""" Entry point for model infering. """


from model.composer import Composer


def main():
    composer = Composer("data/best_model/model", "data/best_model/model.meta",
                        "data/best_model/encoder.dict",
                        "data/best_model/decoder.dict")
    print(
        composer.compose(
            "~e3d efg2|~e3f gedB|~e3d efg2|G2AB gedB|\n", 300
        )
    )


if __name__ == "__main__":
    main()
