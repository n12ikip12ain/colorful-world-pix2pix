# Colorful world - pix2pix implementation

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://colorful-world.herokuapp.com/)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SachaIZADI/colorful-world-pix2pix/blob/master/pix2pix.ipynb)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-no-red.svg)]()


<img src = "/media/color_evolution.gif" height="250">       <img src = "/media/examples.gif" height="250">

**Currently in progress:** 
- Simple web interface for calling the model
- Colab Notebook Cleaning

## The project

The objective of this project is to translate gray-scale pictures into their colorized version. The problem consists in learning
a mapping between the space of grayscale images (`NxNx1` tensors) to the space of RGB images (`NxNx3` tensors).

<img src = "/media/problem_statement.png" height="250">

To do so, we trained a generative model (a [pix2pix](https://phillipi.github.io/pix2pix/) model to be exact) with thousands of pairs of `(grayscale_image, colored_image)`.

This was initially a [school project](https://github.com/SachaIZADI/Colorful-World) from my 2018 DeepLearning class by [Marc Lelarge](https://mlelarge.github.io/dataflowr-web/).
At that time we struggled to implement the model in `pytorch` and we went for `tensorflow` instead. With a bit more experience, I gave this project a fresh start again. 


## Data:
We trained our pix2pix model with face pictures from the open-source dataset [*Labeled Faces in the Wild*](http://vis-www.cs.umass.edu/lfw/) (LFW). 
It contains more than 13,000 images of faces collected from the web.

To download the dataset you can use the shell script [`colorful-world/data/download_data.sh`](https://github.com/SachaIZADI/colorful-world-pix2pix/blob/master/colorful_world/data/download_data.sh) 

```
cd colorful_world/data
download_data.sh
```

We designed a `pytorch Dataset` to handle the generation of training samples. 
It takes a colored image and transforms it into a black & white image.

<img src = "/media/color2black&white.png" height="250">


## Model:
This repo is largely inspired by the paper [*Image-to-Image Translation with Conditional Adversarial Networks*](https://arxiv.org/pdf/1611.07004.pdf)
published in 2016 by Phillip Isola, Jun-Yan Zhu, Tinghui Zhou and Alexei A. Efros.

We built a conditional Generative Adversarial Network (cGAN) made of:
- a generator `G` taking a black&white image as input and generating a colorized version of this image (conditioned on the B&W image),
- a discriminator `D` taking a black&white image and a colorized image (either ground truth or generated by `G`). 
It predicts, **conditionally** to the B&W image if the colorized input is the ground truth or a generated example.

<img src = "/media/GAN.png" height="150">


The generator has a UNet architecture. This architecture is often used for image segmentation, and you could justify that this architecture
helps the generator avoid coloring beyond the edges of the B&W image. A bit like a child. The UNet is a variation of the classical autoencoder.

<img src = "/media/color_edge.jpg" height="150"> <img src = "/media/Unet.png" height="150">

The `pytorch` computational graph of the model is: 

<img src = "/media/generator.png" height="200">

The discriminator is a classical Convet classifier that takes both a B&W and a colored image as input:
<img src = "/media/discriminator.png" height="200">

## Training algorithm

As in the traditional GAN setting, the generator and the discriminator play a Min-Max game. Here our loss function is

<img src = "/media/loss_fn.png" height="20">

That being said, contrary to the pix2pix paper, we did not implement any source of randomness in the generation of the colorized images.
(`z` is fully deterministic in our implementation).

## Results

### Overfitting on a small sample from the dataset

We started by checking that the model could overfit on a small sample (~20 pictures) from the initial dataset. For a batch size of 8, 1000 epochs, 
and learning rates `lr_dis = 1e-6` and `lr_gen = 1e-7` we obtained the following results (left: generated image | right: ground truth) :

<img src = "/media/first_results/img_1_generated.png" height="100"><img src = "/media/first_results/img_1_original.jpg" height="100"> 
<img src = "/media/first_results/img_2_generated.png" height="100"><img src = "/media/first_results/img_2_original.jpg" height="100">

Besides some artifacts and patches that do not seem to be colored (which are all located on the left part of the faces), we obtained satisfying results
that convinced us that the model had indeed the ability to learn a mapping from B&W images to colored ones.

We also observed a typical GAN loss graph with an explicit trade-off between the Generator and the Discriminator during the training.

<img src = "/media/first_results/loss_graph.png" height="200">

As a sanity check, we tried early stopping the training process when the generator loss is at its lowest point. But it proved to be that this loss was artificially
low due to the discriminator not being trained enough (we indeed gave the discriminator 1/10 the learning rate of the generator). See the results below (left: early stopping
at ~100 epochs | right: training for 1000 epochs):

<img src = "/media/first_results/img_1_early_stopping.png" height="100"> <img src = "/media/first_results/img_1_generated.png" height="100">


We also tried our model on an example that was not in the training set, as expected the results are slightly less convincing due to the model's overfitting:

<img src = "/media/first_results/test_img_generated.png" height="100"><img src = "/media/first_results/test_img_original.jpg" height="100">


### Training on a bigger dataset

We eventually trained our model on a bigger dataset, we sampled 2000 images from the LFW dataset and trained it for ~5h 
(I believe that a significant amount of this time is due to the model checkpoints (we saved the model after each epoch -
 don't do this if not needed) on Google Colab. Colab only offered us a single GPU with limited memory (it could fit our
models - the generator being the heaviest one - and a batch of only 16 images of size 512x512).

The final configuration parameters we used are:

```python
config = Config(
    lr_dis = 1e-6,
    lr_gen = 1e-5,
    n_epochs = 60,
    batch_size = 16,
)
``` 

Our results:

- Again, we obtained the typical loss curve of a GAN training:

<img src = "/media/loss_curve.png" height="200">

- We visualized the evolution during training of the colorization of an example from outside the train set.

<img src = "/media/color_evolution.gif" height="250">

We believe that with more training (definitely painful on Colab) the results would be much better. Indeed, the less homogeneous parts of the face (eyes, mouth)
are worse captured by the model than cheeks or hair. Another hint is that the loss curves are not plateauing yet.


## Model deployment

We developed a [Flask app](https://github.com/SachaIZADI/colorful-world-pix2pix/tree/master/api) to deploy the generator model.
It offers: 
- a very basic front-end to have a simple UI to play with the model
- one API endpoint to POST a grayscale image and get its colorized version
- one API endpoint to POST an image and check if it is an actual grayscale image (encoded as a grayscale 8-bit image).
We did implement a feature to catch grayish images encoded as RGB ones, but the model is supposed to take grayscale 8-bit
encoded images only as inputs.

This Flask app was deployed on Heroku (Free Tier plan) and is accessible [here](https://colorful-world.herokuapp.com/). Note that there 
is no GPU available for inference and that it might take a few seconds for the server to reboot.

You should first ping the server by hitting the `/ping` endpoint:

```bash
curl -X GET https://colorful-world.herokuapp.com/ping
```

You can directly call the API with `curl`:
```bash
curl -X POST -F "image=@src_image_path.jpg" https://colorful-world.herokuapp.com/colorize -o "dst_image_path.png"

curl -X POST -F "image=@src_image_path.jpeg" https://colorful-world.herokuapp.com/colorize -o "dst_image_path.png"

curl -X POST -F "image=@src_image_path.jpg" https://colorful-world.herokuapp.com/colorize -o "dst_image_path.png"
```

You can also deploy on your local machine:

```
python3 api/app.py

---------------------------------------------------------------------

 * Serving Flask app "app" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```


## Reproduce the project

1/ Clone the repo and install the dependencies
```
git clone https://github.com/SachaIZADI/colorful-world-pix2pix.git
cd colorful-world-pix2pix
pip install -r requirements.txt
```

2/ Download the data
```
cd colorful_world/data
download_data.sh
```

3/ Train a model

We strongly advise you to use a GPU to train the model from scratch. Hopefully, Google Colab has your back if you want 
to have access to a free GPU. You just need to follow the steps mentioned in the Colab notebok: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SachaIZADI/colorful-world-pix2pix/blob/master/pix2pix.ipynb)

We did not train our model in a fully satisfying way, but we would recommend using these parameters:

```python
config = Config(
    lr_dis = 1e-6,
    lr_gen = 1e-5,
    n_epochs = 200,
    batch_size = 32,
)
``` 

4/ Download our pre-trained model (60 epochs on 2000 examples from LFW)
```bash
cd colorful_world/api/model
download_model.sh
```

5/ Deploying on Heroku

```bash
heroku create [YOUR PROJECT NAME]
git push heroku master
```

*Note to myself - other useful Heroku commands*

```bash
heroku ps:scale web=1
heroku run bash
heroku login
heroku logout
```