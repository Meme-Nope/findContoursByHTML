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

    def _convert_to_s_channel(self) -> np.ndarray:
        kx, ky = self.k_size
        kx = max(3, kx); ky = max(3, ky)
        if kx % 2 == 0: kx += 1
        if ky % 2 == 0: ky += 1
        sigma = 0.0 if self.sigma_x < 0 else float(self.sigma_x)
        blurred = cv2.GaussianBlur(self.image, (kx, ky), sigma)
        hls = cv2.cvtColor(blurred, cv2.COLOR_BGR2HLS)
        return hls[:, :, 2]
    
    def _show_histogram(self, s_channel: np.ndarray, save_path: str) -> None:
        import matplotlib.pyplot as plt
        hist = cv2.calcHist([s_channel], [0], None, [256], [0, 256])
        plt.plot(hist, color='magenta')
        plt.title("Saturation Channel")
        plt.xlabel("Saturation Value")
        plt.ylabel("Frequency")
        plt.grid()
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()


    def _binarize(self, s_channel: np.ndarray,
                  method: str = "inRange", lower: int = 100, upper: int = 200) -> np.ndarray:
        if method == "inRange":
            lo = max(0, min(255, int(lower)))
            up = max(0, min(255, int(upper)))
            if lo > up: lo, up = up, lo
            return cv2.inRange(s_channel, lo, up)
        elif method == "otsu":
            _, binary = cv2.threshold(s_channel, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
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
                                     method: str = "otsu",
                                     lower: int = 100,
                                     upper: int = 200) -> np.ndarray:
        s_channel = self._convert_to_s_channel()
        binary = self._binarize(s_channel, method=method, lower=lower, upper=upper)
        mask = self._extract_largest_contour_mask(binary)
        mask_inv = cv2.bitwise_not(mask)
        self.processed_image = cv2.bitwise_and(self.image, self.image, mask=mask_inv)
        return self.processed_image

    def save(self, save_path: str) -> None:
        if self.processed_image is None:
            raise RuntimeError("先に remove_background_by_contour() を実行してください")
        cv2.imwrite(save_path, self.processed_image)
