from api.datasets.dataset import Dataset
from api.tracer import Tracer

if __name__ == "__main__":
    dataset_name = "WARC"
    artifact_pairs = [("NFR11.txt", "FR41.txt"), ("FR41.txt", "SRS79.txt")]

    for source_id, target_id in artifact_pairs:
        technique_template = "(. (VSM NT) (%d %d))"

        dataset = Dataset(dataset_name)
        source_level_index, source_index = dataset.get_artifact_level_index(source_id)
        print(source_index)
        target_level_index, target_index = dataset.get_artifact_level_index(target_id)
        technique_name = technique_template % (source_level_index, target_level_index)

        tracer = Tracer()
        technique_data = tracer.get_technique_data(dataset_name, technique_name)

        similarity_score = technique_data.similarity_matrix[source_index, target_index]
        print(f"{source_id}-{target_id}: {similarity_score}")
