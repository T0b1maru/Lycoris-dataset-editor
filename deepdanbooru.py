from __future__ import annotations

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import logging
logging.getLogger('tensorflow').setLevel(logging.FATAL)
import argparse

#!/usr/bin/env python

import os
import pathlib
import tarfile
import deepdanbooru as dd
import huggingface_hub
import numpy as np
import PIL.Image
import tensorflow as tf

def load_sample_image_paths() -> list[pathlib.Path]:
    image_dir = pathlib.Path('images')
    if not image_dir.exists():
        path = huggingface_hub.hf_hub_download(
            'public-data/sample-images-TADNE',
            'images.tar.gz',
            repo_type='dataset')
        with tarfile.open(path) as f:
            f.extractall()
    return sorted(image_dir.glob('*'))

def load_model() -> tf.keras.Model:
    path = huggingface_hub.hf_hub_download('public-data/DeepDanbooru',
                                           'model-resnet_custom_v3.h5')
    model = tf.keras.models.load_model(path)
    return model

def load_labels() -> list[str]:
    path = huggingface_hub.hf_hub_download('public-data/DeepDanbooru',
                                           'tags.txt')
    with open(path, 'rt') as f:
        return f.read().splitlines()

def predict(image_path: str, threshold: float):
    model = load_model()
    labels = load_labels()
    image = PIL.Image.open(image_path)
    image = tf.image.resize(image, [512, 512])
    image = np.asarray(image, np.float32) / 255
    if image.shape[-1] == 4:
        image = image[:, :, :3]
    
    # Ensure image is in RGB mode and check its shape before prediction
    if image.shape[-1] != 3:
        raise ValueError(f"Image shape is not as expected. Shape found: {image.shape}")
    scores = model.predict(np.array([image]), verbose=0)[0]

    results = [(label, score) for label, score in zip(labels, scores) if score > threshold]
    
    if args.verbose:
        print(results)
    else:
        tags_only = ', '.join([tag[0] for tag in results])
        
    # Exclude tags based on exclude.txt
    excluded_tags = []
    if os.path.exists('exclude.txt'):
        with open('exclude.txt', 'r') as f:
            excluded_tags = [line.strip() for line in f]
    
    for tag in excluded_tags:
        tags_only = tags_only.replace(tag, '').replace(' ,', '').replace(', ,', ',').strip(', ')

    
    # Exclude tags based on --ignore parameter or exclude.txt
    excluded_tags = []
    if args.ignore:
        excluded_tags = [tag.strip() for tag in args.ignore.split(',')]
    elif os.path.exists('exclude.txt'):
        with open('exclude.txt', 'r') as f:
            excluded_tags = [line.strip() for line in f]
    
    final_output = tags_only
    for tag in excluded_tags:
        final_output = final_output.replace(tag, '').replace(' ,', '').replace(', ,', ',').strip(', ')
    print(final_output)

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='DeepDanbooru CLI Image Prediction')
    parser.add_argument('--image', required=True, help='Path to the image for prediction')
    
    parser.add_argument('--threshold', type=float, default=0.5, help='Score threshold for displaying tags')
    
    parser.add_argument('--verbose', action='store_true', help='Display tags with their scores')
    parser.add_argument('--ignore', type=str, help='Comma separated list of tags to exclude from the output')
    
    
    args = parser.parse_args()
    
    predict(args.image, args.threshold)
