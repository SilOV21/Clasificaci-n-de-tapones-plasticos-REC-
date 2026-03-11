// =============================================================================
// LRA Vision Package - Image Processor
// Image processing utilities for cap detection and classification
// ROS2 Jazzy Jalisco - C++17
// =============================================================================
/**
 * @file image_processor.hpp
 * @brief Image processing utilities for the REC project.
 * 
 * This module provides image processing functions for:
 * - Color space conversions
 * - Thresholding and segmentation
 * - Contour detection
 * - Object detection (plastic caps)
 * - Image preprocessing for classification
 * 
 * @author Dr. Asil
 * @date March 2026
 * @copyright MIT License
 */

#ifndef LRA_VISION__IMAGE_PROCESSOR_HPP_
#define LRA_VISION__IMAGE_PROCESSOR_HPP_

#include <string>
#include <vector>
#include <optional>
#include <memory>

#include <opencv2/opencv.hpp>
#include <opencv2/imgproc.hpp>

namespace lra_vision
{

/**
 * @struct DetectedObject
 * @brief Represents a detected object in an image.
 */
struct DetectedObject
{
  cv::Rect bounding_box;           ///< Bounding rectangle
  cv::Point2f center;              ///< Center point
  double area;                     ///< Area in pixels
  double perimeter;                ///< Perimeter in pixels
  double circularity;              ///< Circularity measure (0-1)
  cv::Moments moments;             ///< Image moments
  cv::RotatedRect rotated_rect;    ///< Rotated bounding rectangle
  std::string color_class;         ///< Color classification
  cv::Scalar mean_color;           ///< Mean color in BGR
  double confidence;               ///< Detection confidence (0-1)
};

/**
 * @struct ColorRange
 * @brief Defines a color range in HSV space.
 */
struct ColorRange
{
  std::string name;                ///< Color name
  cv::Scalar lower;                ///< Lower HSV bounds
  cv::Scalar upper;                ///< Upper HSV bounds
  cv::Scalar display_color;        ///< BGR color for display
  
  /**
   * @brief Create a color range from name and bounds.
   */
  static ColorRange create(
    const std::string& name,
    int h_low, int s_low, int v_low,
    int h_high, int s_high, int v_high,
    const cv::Scalar& display = cv::Scalar(255, 255, 255)
  );
};

/**
 * @struct ProcessingParams
 * @brief Parameters for image processing pipeline.
 */
struct ProcessingParams
{
  // Gaussian blur parameters
  int blur_kernel_size = 5;
  double blur_sigma = 1.5;
  
  // Thresholding parameters
  int threshold_type = cv::THRESH_BINARY + cv::THRESH_OTSU;
  double threshold_value = 128.0;
  
  // Morphological operations
  int morph_kernel_size = 3;
  int morph_iterations = 2;
  
  // Contour filtering
  double min_contour_area = 500.0;
  double max_contour_area = 50000.0;
  double min_circularity = 0.6;
  double max_circularity = 1.1;
  
  // Color detection (HSV ranges)
  std::vector<ColorRange> color_ranges;
  
  /**
   * @brief Initialize with default color ranges for plastic caps.
   */
  static ProcessingParams default_for_caps();
  
  /**
   * @brief Load from YAML file.
   */
  static ProcessingParams from_yaml(const std::string& filepath);
};

/**
 * @class ImageProcessor
 * @brief Image processing pipeline for plastic cap detection.
 * 
 * Provides a complete pipeline for detecting and classifying
 * plastic caps in images:
 * 1. Preprocessing (blur, color conversion)
 * 2. Segmentation (thresholding, morphological operations)
 * 3. Contour detection
 * 4. Object filtering
 * 5. Color classification
 * 
 * @example
 * @code
 * ProcessingParams params = ProcessingParams::default_for_caps();
 * ImageProcessor processor(params);
 * 
 * cv::Mat image = cv::imread("caps.jpg");
 * auto objects = processor.detect_objects(image);
 * 
 * for (const auto& obj : objects) {
 *   std::cout << "Detected " << obj.color_class << " cap at " 
 *             << obj.center << std::endl;
 * }
 * @endcode
 */
class ImageProcessor
{
public:
  /**
   * @brief Construct processor with parameters.
   * @param params Processing parameters.
   */
  explicit ImageProcessor(const ProcessingParams& params = ProcessingParams::default_for_caps());
  
  // ========================================================================
  // Main Processing Functions
  // ========================================================================
  
  /**
   * @brief Detect all objects (caps) in an image.
   * @param image Input image (BGR format).
   * @return Vector of detected objects.
   */
  std::vector<DetectedObject> detect_objects(const cv::Mat& image);
  
  /**
   * @brief Detect objects of a specific color.
   * @param image Input image.
   * @param color_name Color name to detect.
   * @return Vector of detected objects of the specified color.
   */
  std::vector<DetectedObject> detect_objects_by_color(
    const cv::Mat& image,
    const std::string& color_name
  );
  
  /**
   * @brief Classify the color of an image region.
   * @param image Input image.
   * @param roi Region of interest.
   * @return Color classification string.
   */
  std::string classify_color(const cv::Mat& image, const cv::Rect& roi);
  
  // ========================================================================
  // Preprocessing Functions
  // ========================================================================
  
  /**
   * @brief Preprocess image for detection.
   * @param image Input image.
   * @return Preprocessed image.
   */
  cv::Mat preprocess(const cv::Mat& image) const;
  
  /**
   * @brief Convert image to HSV color space.
   * @param image BGR image.
   * @return HSV image.
   */
  cv::Mat to_hsv(const cv::Mat& image) const;
  
  /**
   * @brief Apply Gaussian blur.
   * @param image Input image.
   * @return Blurred image.
   */
  cv::Mat blur(const cv::Mat& image) const;
  
  /**
   * @brief Apply morphological operations (opening/closing).
   * @param image Binary image.
   * @return Morphologically processed image.
   */
  cv::Mat morphological_process(const cv::Mat& image) const;
  
  // ========================================================================
  // Segmentation Functions
  // ========================================================================
  
  /**
   * @brief Create binary mask for a color range.
   * @param hsv_image HSV image.
   * @param color_range Color range definition.
   * @return Binary mask.
   */
  cv::Mat create_color_mask(const cv::Mat& hsv_image, const ColorRange& color_range) const;
  
  /**
   * @brief Threshold image.
   * @param image Grayscale image.
   * @return Binary thresholded image.
   */
  cv::Mat threshold(const cv::Mat& image) const;
  
  /**
   * @brief Detect edges using Canny algorithm.
   * @param image Input image.
   * @param low_threshold Lower threshold.
   * @param high_threshold Upper threshold.
   * @return Edge image.
   */
  cv::Mat detect_edges(const cv::Mat& image, double low_threshold = 50, double high_threshold = 150) const;
  
  // ========================================================================
  // Contour Detection Functions
  // ========================================================================
  
  /**
   * @brief Find contours in a binary image.
   * @param binary Binary image.
   * @return Vector of contours.
   */
  std::vector<std::vector<cv::Point>> find_contours(const cv::Mat& binary) const;
  
  /**
   * @brief Filter contours based on area and circularity.
   * @param contours Input contours.
   * @return Filtered contours.
   */
  std::vector<std::vector<cv::Point>> filter_contours(
    const std::vector<std::vector<cv::Point>>& contours
  ) const;
  
  /**
   * @brief Convert contour to DetectedObject.
   * @param contour Input contour.
   * @param image Original image for color analysis.
   * @return DetectedObject structure.
   */
  DetectedObject contour_to_object(
    const std::vector<cv::Point>& contour,
    const cv::Mat& image
  ) const;
  
  // ========================================================================
  // Visualization Functions
  // ========================================================================
  
  /**
   * @brief Draw detected objects on image.
   * @param image Input image.
   * @param objects Detected objects.
   * @return Visualization image.
   */
  cv::Mat draw_detections(
    const cv::Mat& image,
    const std::vector<DetectedObject>& objects
  ) const;
  
  /**
   * @brief Draw color masks overlay.
   * @param image Original image.
   * @param masks Color masks for each color.
   * @return Overlay image.
   */
  cv::Mat draw_color_masks(
    const cv::Mat& image,
    const std::map<std::string, cv::Mat>& masks
  ) const;
  
  // ========================================================================
  // Utility Functions
  // ========================================================================
  
  /**
   * @brief Calculate circularity of a contour.
   * @param contour Input contour.
   * @return Circularity value (0-1, where 1 is a perfect circle).
   */
  static double calculate_circularity(const std::vector<cv::Point>& contour);
  
  /**
   * @brief Get mean color of a region.
   * @param image Input image.
   * @param mask Mask defining the region.
   * @return Mean color (BGR).
   */
  static cv::Scalar get_mean_color(const cv::Mat& image, const cv::Mat& mask);
  
  /**
   * @brief Get parameters.
   * @return Current processing parameters.
   */
  const ProcessingParams& get_params() const { return params_; }
  
  /**
   * @brief Set parameters.
   * @param params New processing parameters.
   */
  void set_params(const ProcessingParams& params) { params_ = params; }
  
  /**
   * @brief Add a color range for detection.
   * @param color_range Color range to add.
   */
  void add_color_range(const ColorRange& color_range);
  
  /**
   * @brief Clear all color ranges.
   */
  void clear_color_ranges();

private:
  ProcessingParams params_;
  
  /**
   * @brief Initialize default color ranges for plastic caps.
   */
  void initialize_default_colors();
};

}  // namespace lra_vision

#endif  // LRA_VISION__IMAGE_PROCESSOR_HPP_