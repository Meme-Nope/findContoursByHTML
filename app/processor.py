import cv2
import numpy as np
from typing import Optional


class ImageProcessor:
    def __init__(self, image_path: str,
                 k_size: tuple[int, int] = (3, 3),
                 sigma_x: float = -1):
        self.image_path = image_path
        self.k_size = k_size
        self.sigma_x = sigma_x
        self.image = self._load_image()
        self.processed_image = None


    def _load_image(self) -> Optional[np.ndarray]:
        img = cv2.imread(self.image_path)
        if img is None:
            raise ValueError(f"画像を読み込めませんでした: {self.image_path}")
        return img

    def _convert_to_l_channel(self) -> np.ndarray:
        blurred = cv2.GaussianBlur(self.image,self.k_size, self.sigma_x)
        hls = cv2.cvtColor(blurred, cv2.COLOR_BGR2HLS)
        return  hls[:, :, 1]
    
    def _show_histogram(self, l_channel: np.ndarray, save_path: str) -> None:
        import matplotlib.pyplot as plt
        hist = cv2.calcHist([l_channel], [0], None, [256], [0, 256])
        plt.plot(hist, color='magenta')
        plt.title("L Channel Histogram")
        plt.xlabel("L Value")
        plt.ylabel("Frequency")
        plt.grid()
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()


    def _binarize(self, l_channel: np.ndarray,
                  method: str = "inRange", lower: int = 100, upper: int = 200) -> np.ndarray:
        if method == "inRange":
            return cv2.inRange(l_channel, lower, upper)
        elif method == "otsu":
            _, binary = cv2.threshold(l_channel, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            return binary
        else:
            raise ValueError(f"不明な2値化メソッド: {method}")

    def _extract_largest_contour_mask(self, binary: np.ndarray) -> np.ndarray:
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            raise ValueError("輪郭が見つかりませんでした")
        largest = max(contours, key=cv2.contourArea)
        mask = np.zeros_like(binary)
        cv2.drawContours(mask, [largest], -1, 255, thickness=cv2.FILLED)
        return mask

    def remove_background_by_contour(self,
                                     method: str = "inRange",
                                     lower: int = 100,
                                     upper: int = 200) -> np.ndarray:
        l_channel = self._convert_to_l_channel()
        binary = self._binarize(l_channel, method=method, lower=lower, upper=upper)
        mask = self._extract_largest_contour_mask(binary)
        mask_inv = cv2.bitwise_not(mask)
        self.processed_image = cv2.bitwise_and(self.image, self.image, mask=mask_inv)
        return self.processed_image

    def save(self, save_path: str) -> None:
        if self.processed_image is None:
            raise RuntimeError("先に remove_background_by_contour() を実行してください")
        cv2.imwrite(save_path, self.processed_image)
