import os
import tensorflow.keras as keras
import matplotlib.pyplot as plt
from tensorflow.keras.applications.xception import Xception
from tensorflow.keras import layers
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping

PATH = r'../input/hand-sign-recognition/original_images/original_images'

classes_wo_digits = os.listdir(PATH)

classes_wo_digits.sort()

classes_wo_digits = classes_wo_digits[10:]

print(classes_wo_digits)

datagen = keras.preprocessing.image.ImageDataGenerator(
                                            rescale=1./255,
                                            validation_split=0.2
                                                       )

train_generator = datagen.flow_from_directory(
                                        PATH,
                                        target_size=(256, 256),
                                        seed=51,
                                        subset='training',
                                        classes=classes_wo_digits
                                              )

validation_generator = datagen.flow_from_directory(
                                        PATH,
                                        target_size=(256, 256),
                                        seed=51,
                                        subset='validation',
                                        shuffle=False,
                                        classes=classes_wo_digits
                                                   )

fig, axes = plt.subplots(4, 8, sharex=True, figsize=(10, 10))

plt.subplots_adjust(bottom=0.1, left=0.01, right=0.99,
                    top=0.9, hspace=0.35)

for i in range(4):
    for j in range(8):
        plt.gray()
        axes[i, j].imshow(train_generator[0][0][8*i + j])
        axes[i, j].set_title(
          classes_wo_digits[
              train_generator[0][1][8*i + j].argmax()
                            ],
          weight='bold', size=16)
        axes[i, j].set_xticks([])
        axes[i, j].set_yticks([])

plt.show()

xception = Xception(include_top=False, input_shape=(256, 256, 3))

x = xception.output
x = layers.GlobalMaxPooling2D()(x)
x = layers.Dense(1024, activation='relu')(x)
x = layers.Dense(512, activation='relu')(x)
output = layers.Dense(31, activation='softmax')(x)

model = Model(xception.input, output)

# Freezing all the Imported Layers
for layers in xception.layers:
    layers.trainable = False

model.compile(optimizer='adam', loss="categorical_crossentropy",
              metrics=["accuracy"])

earlystop = EarlyStopping(monitor='val_accuracy', patience=20,
                          verbose=1)

hist = model.fit(train_generator,
                 validation_data=validation_generator,
                 steps_per_epoch=100, validation_steps=10,
                 epochs=50, callbacks=[earlystop])

plt.figure(figsize=(8,6))
plt.plot(hist.history["accuracy"])
plt.plot(hist.history['val_accuracy'])
plt.plot(hist.history['loss'])
plt.plot(hist.history['val_loss'])
plt.title("Model Metrics", weight='bold', size=18)
plt.ylabel("Accuracy / Loss", size=14)
plt.xlabel("Epoch", size=14)
plt.legend(["Training Accuracy", "Validation Accuracy",
            "Training Loss", "Validation Loss"])
plt.show()

result = model.evaluate(validation_generator, steps=280)