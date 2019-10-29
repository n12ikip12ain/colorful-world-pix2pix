# Colorful world - pix2pix implementation

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SachaIZADI/colorful-world-pix2pix/blob/master/pix2pix.ipynb)

## Data:
We trained our Colorizer model with face picture from the open-source dataset [*Labeled Faces in the Wild*](http://vis-www.cs.umass.edu/lfw/) (LFW). 
It contains more than 13,000 images of faces collected from the web.

To download the dataset you can use the shell script from `colorful-world/data/download_data.sh` 

```
cd colorful_world/data
chmod +x download_data.sh #Rq: you might not need this
download_data.sh
```

We designed a `pytorch Dataset` to handle the generation of training samples. 
It takes a colored image and transforms it into a black & white image.

<img src = "/media/color2black&white.png" height="250">


## Model:
This repo is largely inspired by the paper [*Image-to-Image Translation with Conditional Adversarial Networks*](https://arxiv.org/pdf/1611.07004.pdf)
published in 2016 by Phillip Isola, Jun-Yan Zhu, Tinghui Zhou and Alexei A. Efros.

We build a conditional Generative Adversarial Network (cGAN) made of:
- a generator `G` taking a black&white image as input and generating a colorized version of this image (conditioned on the image)
- a discriminator `D` taking a black&white image and a colorized image (either ground truth or generated by `G`). 
It predicts, **conditionally** to the B&W image if the colorized input is the ground truth or a generated example.

<img src = "/media/GAN.png" height="100">


The generator has a UNet architecture. This architecture is often used for image segmentation, and one could justify that this architecture
helps the generator avoid coloring beyond the edges of the B&W image. A bit like a child.

<img src = "/media/color_edge.jpg" height="150">

It is a variation of the classical autoencoder:

<img src = "/media/Unet.png" height="150">

The `pytorch` computational graph of the model is: 

<img src = "/media/generator.png" height="200">

The discriminator is a classical Convet classifier that takes both a B&W and a colored image as input:
<img src = "/media/discriminator.png" height="200">

## Training algorithm

As in the traditional GAN setting, the generator and the discriminator play a Min-Max game. Here our loss function is
<img src = "/media/loss_fn.png" height="20">

That being said, contrary to the pix2pix paper, we did not implement any source of randomness in the generation of the colorized images.

## Results

### Overfitting on a small sample from the dataset

We started by checking that the model could overfit on a small sample (~20 pictures) from the initial dataset. For a batch size of 8, 1000 epochs, 
and learning rates `lr_dis = 1e-6` and `lr_gen = 1e-7` we obtained the following results (left: generated image | right: ground truth) :

<img src = "/media/first_results/img_1_generated.png" height="100"><img src = "/media/first_results/img_1_original.png" height="100">

<img src = "/media/first_results/img_2_generated.png" height="100"><img src = "/media/first_results/img_2_original.png" height="100">

Besides some artifacts and patches that do not seem to be colored (which are all located on the left part of the faces), we obtained satisfying results
that convinced us that the model had indeed the ability to learn a mapping from B&W images to colored ones.

We also observed a typical GAN loss graph with an explicit trade-off between the Generator and the Discriminator during the training.

<img src = "/media/first_results/loss_graph.png" height="200">

We also tried our model on an example that was not in the training set, as expected the results are less convincing due to the model's overfitting:

<img src = "/media/first_results/test_img_generated.png" height="100"><img src = "/media/first_results/test_img_original.png" height="100">


### Training on a bigger dataset


<img src = "/colorful_world/results/loss_graph.png" height="200">

<img src = "/colorful_world/results/color_evolution/colorization_training.gif" height="200">


## Reproduce the project

# TODO:

https://medium.com/@ashwindesilva/how-to-use-google-colaboratory-to-clone-a-github-repository-e07cf8d3d22b
https://stackoverflow.com/questions/48350226/methods-for-using-git-with-google-colab
    
- Work with collab
    - create a script to clone the project
    - create a script to launch the training

- Pay a AWS server to train / and predict



- Make a Flask API & deploy in serverless
