# flake8: noqa

from os.path import abspath
from pathlib import Path
import json

from rastervision.core.rv_pipeline import *
from rastervision.core.backend import *
from rastervision.core.data import *
from rastervision.core.analyzer import *
from rastervision.pytorch_backend import *
from rastervision.pytorch_learner import *
from rastervision.pytorch_backend.examples.utils import read_stac

image_uri = './jacksonville.sub.tif'


def get_config(runner, output_dir: str, stac_export_uri: str,
               **kwargs: dict) -> ChipClassificationConfig:
    """Generate the pipeline config for this task. This function will be called
    by RV, with arguments from the command line, when this example is run.

    Args:
        runner (Runner): Runner for the pipeline. Will be provided by RV.
        output_dir (str): Directory where all the output will be written.

    Returns:
        ChipClassificationConfig: A pipeline config.
    """
    stac_unzip_dir = f'./tmp/{Path(stac_export_uri).stem}'
    scene_infos = read_stac(stac_export_uri, stac_unzip_dir)

    chip_sz = int(kwargs.get('chip_sz', 300))
    img_sz = int(kwargs.get('img_sz', chip_sz))

    def make_scene(id: str, info: dict) -> SceneConfig:
        return SceneConfig(
            id=id,
            raster_source=RasterioSourceConfig(
                uris=[abspath(image_uri)], channel_order=[0, 1, 2]),
            label_source=ChipClassificationLabelSourceConfig(
                vector_source=GeoJSONVectorSourceConfig(
                    uri=info['label_uri'],
                    default_class_id=1,
                    ignore_crs_field=True),
                infer_cells=True,
                ioa_thresh=0.5,
                use_intersection_over_cell=False,
                pick_min_class_id=False,
                background_class_id=0),
            aoi_geometries=[info['aoi_geometry']])

    class_config = ClassConfig(names=['background', 'boat'])

    scene_dataset = DatasetConfig(
        class_config=class_config,
        train_scenes=[
            make_scene(id=f'train-{i}', info=info)
            for i, info in enumerate(scene_infos)
        ],
        validation_scenes=[
            make_scene(id=f'val-{i}', info=info)
            for i, info in enumerate(scene_infos)
        ])

    data = ClassificationGeoDataConfig(
        scene_dataset=scene_dataset,
        window_opts=GeoDataWindowConfig(
            method=GeoDataWindowMethod.random,
            size=chip_sz,
            max_windows=int(kwargs.get('chips_per_scene', 100)),
        ),
        img_sz=img_sz,
        num_workers=4)

    backend = PyTorchChipClassificationConfig(
        data=data,
        model=ClassificationModelConfig(
            backbone=Backbone.resnet18,
            init_weights=kwargs.get('init_weights', None)),
        solver=SolverConfig(
            lr=float(kwargs.get('lr', 1e-3)),
            num_epochs=int(kwargs.get('num_epochs', 5)),
            batch_sz=int(kwargs.get('batch_sz', 32))),
        log_tensorboard=False,
        run_tensorboard=False)

    pipeline = ChipClassificationConfig(
        root_uri=output_dir,
        dataset=scene_dataset,
        backend=backend,
        train_chip_sz=chip_sz,
        predict_chip_sz=300)

    return pipeline
