from flask import Flask, jsonify, request, send_file
from PIL import Image
import io
import numpy as np
import torch


app = Flask(__name__)

IMAGE_SIZE = 512

# TODO: here
#PATH_TO_MODEL = "../colorful_world/models_saved/xxx.pkl"
#generator = torch.load(PATH_TO_MODEL)

generator = None


@app.route('/', methods=['GET'])
def home():
    return


@app.route('/check_image', methods=['POST'])
def check_image():
    if request.files.get("image"):

        image = request.files["image"].read()
        image = Image.open(io.BytesIO(image))
        input_array = np.asarray(image)

        return jsonify({
            "image_shape": input_array.shape,
            "is_grayscale_image": len(input_array.shape) == 2,
        })


@app.route('/test', methods=['POST'])
def test():
    if request.files.get("image"):

        input_img = request.files["image"].read()
        input_img = Image.open(io.BytesIO(input_img))

        input_img = input_img.resize((IMAGE_SIZE, IMAGE_SIZE))

        input_img_array = np.asarray(input_img)

        output_img = Image.fromarray(input_img_array)

        output_img_io = io.BytesIO()
        output_img.save(output_img_io, 'PNG')
        output_img_io.seek(0)

        return send_file(output_img_io, mimetype='image/png')


@app.route('/colorize', methods=['POST'])
def colorize():
    if request.files.get("image"):

        input_img = request.files["image"].read()
        input_img = Image.open(io.BytesIO(input_img))

        input_img_shape = input_img.size
        input_img = input_img.resize((IMAGE_SIZE, IMAGE_SIZE))

        input_img_array = np.asarray(input_img)

        if len(input_img_array.shape) != 2:
            response = jsonify({
                "message": "Your image is not a real grayscale image. Please change format."
            })
            response.status_code = 401
            return response

        input_img_array_scaled = ((input_img_array / 256) - 0.5) * 2.0
        input_tensor = torch.from_numpy(input_img_array_scaled).type(torch.FloatTensor).unsqueeze(0)

        output_tensor = generator(input_tensor)

        output_img_array_scaled = output_tensor.cpu().numpy()[0].transpose(1, 2, 0)
        output_img_array = (((output_img_array_scaled / 2.0 + 0.5) * 256).astype('uint8'))
        output_img = Image.fromarray(output_img_array)

        output_img = output_img.resize(input_img_shape)

        output_img_io = io.BytesIO()
        output_img.save(output_img_io, 'PNG')
        output_img_io.seek(0)

        return send_file(output_img_io, mimetype='image/png')

    else:

        response = jsonify({
            "message": "An image file is required"
        })
        response.status_code = 401

        return response


if __name__ == '__main__':
    app.run()
