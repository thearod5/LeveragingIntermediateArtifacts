from api.datasets.builder.dataset_builder import DatasetBuilder
from api.datasets.dataset import Dataset
from api.tracer import Tracer

DATASET_NAME = "IllustrativeExample"
TOP_TECHNIQUE_NAME = "(. (VSM NT) (0 1))"
BOTTOM_TECHNIQUE_NAME = "(. (VSM NT) (1 2))"
DIRECT_TECHNIQUE_NAME = "(. (VSM NT) (0 2))"
TECHNIQUE_NAME = "(x (MAX INDEPENDENT) ((. (VSM NT) (0 1)) (. (VSM NT) (1 2))))"
REBUILD = False

if __name__ == "__main__":
    if REBUILD:
        dataset_builder = DatasetBuilder(DATASET_NAME)
        dataset_builder.build()
        dataset_builder.export()

    dataset = Dataset(DATASET_NAME)

    tracer = Tracer()
    top_technique_data = tracer.get_technique_data(DATASET_NAME, TOP_TECHNIQUE_NAME)
    bottom_technique_data = tracer.get_technique_data(
        DATASET_NAME, BOTTOM_TECHNIQUE_NAME
    )
    direct_technique_data = tracer.get_technique_data(
        DATASET_NAME, DIRECT_TECHNIQUE_NAME
    )

    top_score = top_technique_data.similarity_matrix[0][0]
    bottom_score = bottom_technique_data.similarity_matrix[0][0]
    transitive_score = top_score * bottom_score
    direct_score = direct_technique_data.similarity_matrix[0][0]

    print("TOP:", top_score)
    print("BOTTOM:", bottom_score)
    print("TRANSITIVE:", transitive_score)
    print("DIRECT:", direct_score)
    print("HYBRID:", direct_score + transitive_score)
