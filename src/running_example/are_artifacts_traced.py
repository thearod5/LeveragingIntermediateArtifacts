from api.datasets.dataset import Dataset

if __name__ == "__main__":
    dataset_name = "EBT"
    source_artifact = 151
    target_artifact = 68
    intermediate_artifacts = [132, 135, 127, 113, 134]

    dataset = Dataset(dataset_name)

    for intermediate_artifact in intermediate_artifacts:
        artifacts = [
            (source_artifact, target_artifact, "direct"),
            (source_artifact, intermediate_artifact, "top"),
            (intermediate_artifact, target_artifact, "bottom"),
        ]
        for source_id, target_id, label in artifacts:
            source_level_index, source_index = dataset.get_artifact_level_index(
                source_id
            )
            target_level_index, target_index = dataset.get_artifact_level_index(
                target_id
            )
            trace_id = f"{source_level_index}-{target_level_index}"
            link_id = f"{source_id}-{target_id}"
            link_value = dataset.traced_matrices[trace_id][source_index, target_index]
            print(f"{label}:{link_id}:{link_value}")
        print("")
