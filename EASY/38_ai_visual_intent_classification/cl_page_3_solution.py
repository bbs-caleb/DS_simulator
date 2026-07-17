"""Visual intent classification of user screenshots with a zero-shot CLIP model."""

# pylint: disable=too-few-public-methods  # class API is fixed by the task template

from PIL import Image, UnidentifiedImageError
from transformers import CLIPModel, CLIPProcessor

MODEL_ID = "yujiepan/clip-vit-tiny-random-patch14-336"


class ImageProcessor:
    """
    A class for processing images.

    Attributes:
        image_path (str): The path to the image.
    """

    def __init__(self, image_path: str):
        """
        Initialize an ImageProcessor instance.

        Parameters:
            image_path (str): The path to the image.

        Raises:
            ValueError: If the image path is empty.
        """
        if not image_path:
            raise ValueError("Image path must not be empty.")
        self.image_path = image_path

    def prepare_image(self) -> Image.Image:
        """
        Method to prepare the image for processing.

        Returns:
            Image.Image: The prepared image.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file is not a readable image.
        """
        try:
            image = Image.open(self.image_path)  # keeps format-specific subclass type
        except FileNotFoundError as error:
            raise FileNotFoundError(f"Image not found: {self.image_path}") from error
        except UnidentifiedImageError as error:
            raise ValueError(f"Cannot decode image: {self.image_path}") from error
        except OSError as error:
            raise ValueError(f"Cannot read image: {self.image_path}") from error
        return image


class ClipModel:
    """
    A class for working with a classification model.

    Attributes:
        model (CLIPModel): The CLIP model instance.
        processor (CLIPProcessor): The CLIP processor instance.
    """

    def __init__(self):
        """
        Initialize a ClipModel instance.
        """
        self.model = CLIPModel.from_pretrained(MODEL_ID)  # loaded once, reused
        self.processor = CLIPProcessor.from_pretrained(MODEL_ID)

    def classify(self, image: Image.Image, intents: list) -> list:
        """
        Method for classifying data.

        Parameters:
            image (Image.Image): The image to classify.
            intents (list): The list of text categories.

        Returns:
            list: The classification result as probability distribution.
        """
        inputs = self.processor(
            text=intents,
            images=image,
            return_tensors="pt",
            padding=True,
        )
        outputs = self.model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)  # (1, n_intents)
        return probs.detach().numpy()[0].tolist()


class ImageClassifier:
    """
    A class for classifying images.

    Attributes:
        clip_model (ClipModel): An object for data classification.
        intents (List[str]): A list of categories for classification.
    """

    def __init__(self):
        """
        Initialize an ImageClassifier instance.
        """
        self.clip_model = ClipModel()
        self.intents = ["payment-problem", "course-problem", "profile-problem"]

    def classify_intent(self, image_path: str) -> str:
        """
        Method for classifying intent.

        Parameters:
            image_path (str): The path to the image.

        Returns:
            str: The category of intent.
        """
        image = ImageProcessor(image_path).prepare_image()
        probs = self.clip_model.classify(image, self.intents)
        return self.intents[probs.index(max(probs))]  # argmax over probabilities
