// =============================================================================
// LRA Vision Package - Image Processor Implementation
// Image processing utilities for cap detection and classification
// ROS2 Jazzy Jalisco - C++17
// =============================================================================

#include "lra_vision/image_processor.hpp"

#include <algorithm>
#include <cmath>

namespace lra_vision
{

// =============================================================================
// ColorRange Implementation
// =============================================================================

ColorRange ColorRange::create(
  const std::string& name,
  int h_low, int s_low, int v_low,
  int h_high, int s_high, int v_high,
  const cv::Scalar& display)
{
  ColorRange range;
  range.name = name;
  range.lower = cv::Scalar(h_low, s_low, v_low);
  range.upper = cv::Scalar(h_high, s_high, v_high);
  range.display_color = display;
  return range;
}

// =============================================================================
// ProcessingParams Implementation
// =============================================================================

ProcessingParams ProcessingParams::default_for_caps()
{
  ProcessingParams params;
  
  // Default color ranges for common plastic cap colors
  params.color_ranges = {
    ColorRange::create("red", 0, 100, 50, 10, 255, 255, cv::Scalar(0, 0, 255)),
    ColorRange::create("red2", 170, 100, 50, 180, 255, 255, cv::Scalar(0, 0, 255)),
    ColorRange::create("blue", 100, 100, 50, 130, 255, 255, cv::Scalar(255, 0, 0)),
    ColorRange::create("green", 40, 100, 50, 80, 255, 255, cv::Scalar(0, 255, 0)),
    ColorRange::create("yellow", 20, 100, 50, 40, 255, 255, cv::Scalar(0, 255, 255)),
    ColorRange::create("orange", 10, 100, 50, 20, 255, 255, cv::Scalar(0, 165, 255)),
    ColorRange::create("white", 0, 0, 200, 180, 50, 255, cv::Scalar(255, 255, 255)),
    ColorRange::create("black", 0, 0, 0, 180, 50, 50, cv::Scalar(50, 50, 50)),
  };
  
  return params;
}

ProcessingParams ProcessingParams::from_yaml(const std::string& filepath)
{
  ProcessingParams params = default_for_caps();
  
  // TODO: Implement YAML loading
  (void)filepath;
  
  return params;
}

// =============================================================================
// ImageProcessor Implementation
// =============================================================================

ImageProcessor::ImageProcessor(const ProcessingParams& params)
: params_(params)
{
  if (params_.color_ranges.empty()) {
    initialize_default_colors();
  }
}

void ImageProcessor::initialize_default_colors()
{
  params_.color_ranges = ProcessingParams::default_for_caps().color_ranges;
}

std::vector<DetectedObject> ImageProcessor::detect_objects(const cv::Mat& image)
{
  std::vector<DetectedObject> objects;
  
  // Preprocess image
  cv::Mat hsv = to_hsv(image);
  cv::Mat blurred = blur(hsv);
  
  // Process each color range
  for (const auto& color_range : params_.color_ranges) {
    cv::Mat mask = create_color_mask(blurred, color_range);
    mask = morphological_process(mask);
    
    auto contours = find_contours(mask);
    contours = filter_contours(contours);
    
    for (const auto& contour : contours) {
      DetectedObject obj = contour_to_object(contour, image);
      obj.color_class = color_range.name;
      objects.push_back(obj);
    }
  }
  
  return objects;
}

std::vector<DetectedObject> ImageProcessor::detect_objects_by_color(
  const cv::Mat& image,
  const std::string& color_name)
{
  std::vector<DetectedObject> objects;
  
  // Find the color range
  auto it = std::find_if(params_.color_ranges.begin(), params_.color_ranges.end(),
    [&color_name](const ColorRange& r) { return r.name == color_name; });
  
  if (it == params_.color_ranges.end()) {
    return objects;
  }
  
  cv::Mat hsv = to_hsv(image);
  cv::Mat mask = create_color_mask(hsv, *it);
  mask = morphological_process(mask);
  
  auto contours = find_contours(mask);
  contours = filter_contours(contours);
  
  for (const auto& contour : contours) {
    DetectedObject obj = contour_to_object(contour, image);
    obj.color_class = color_name;
    objects.push_back(obj);
  }
  
  return objects;
}

std::string ImageProcessor::classify_color(const cv::Mat& image, const cv::Rect& roi)
{
  if (roi.x < 0 || roi.y < 0 || 
      roi.x + roi.width > image.cols || 
      roi.y + roi.height > image.rows) {
    return "unknown";
  }
  
  cv::Mat region = image(roi);
  cv::Mat hsv = to_hsv(region);
  
  // Calculate histogram for hue channel
  std::vector<int> hist(180, 0);
  for (int y = 0; y < hsv.rows; ++y) {
    for (int x = 0; x < hsv.cols; ++x) {
      int h = hsv.at<cv::Vec3b>(y, x)[0];
      int s = hsv.at<cv::Vec3b>(y, x)[1];
      int v = hsv.at<cv::Vec3b>(y, x)[2];
      
      if (s > 50 && v > 50) {
        hist[h]++;
      }
    }
  }
  
  // Find dominant hue
  int max_hue = 0;
  int max_count = 0;
  for (int h = 0; h < 180; ++h) {
    if (hist[h] > max_count) {
      max_count = hist[h];
      max_hue = h;
    }
  }
  
  // Classify by hue
  if (max_count < roi.area() * 0.1) {
    // Low saturation - white or gray
    cv::Scalar mean = cv::mean(region);
    if (mean[0] > 200 && mean[1] > 200 && mean[2] > 200) {
      return "white";
    } else if (mean[0] < 50 && mean[1] < 50 && mean[2] < 50) {
      return "black";
    }
    return "gray";
  }
  
  if (max_hue < 10 || max_hue > 170) {
    return "red";
  } else if (max_hue < 20) {
    return "orange";
  } else if (max_hue < 40) {
    return "yellow";
  } else if (max_hue < 80) {
    return "green";
  } else if (max_hue < 100) {
    return "cyan";
  } else if (max_hue < 130) {
    return "blue";
  } else if (max_hue < 150) {
    return "purple";
  } else {
    return "red";
  }
}

cv::Mat ImageProcessor::preprocess(const cv::Mat& image) const
{
  cv::Mat processed;
  
  // Convert to grayscale if needed
  if (image.channels() == 3) {
    cv::cvtColor(image, processed, cv::COLOR_BGR2GRAY);
  } else {
    processed = image.clone();
  }
  
  // Apply Gaussian blur
  processed = blur(processed);
  
  return processed;
}

cv::Mat ImageProcessor::to_hsv(const cv::Mat& image) const
{
  cv::Mat hsv;
  if (image.channels() == 3) {
    cv::cvtColor(image, hsv, cv::COLOR_BGR2HSV);
  } else {
    cv::cvtColor(image, hsv, cv::COLOR_GRAY2BGR);
    cv::cvtColor(hsv, hsv, cv::COLOR_BGR2HSV);
  }
  return hsv;
}

cv::Mat ImageProcessor::blur(const cv::Mat& image) const
{
  cv::Mat blurred;
  cv::GaussianBlur(
    image,
    blurred,
    cv::Size(params_.blur_kernel_size | 1, params_.blur_kernel_size | 1),  // Ensure odd
    params_.blur_sigma
  );
  return blurred;
}

cv::Mat ImageProcessor::morphological_process(const cv::Mat& image) const
{
  cv::Mat processed;
  
  cv::Mat kernel = cv::getStructuringElement(
    cv::MORPH_ELLIPSE,
    cv::Size(params_.morph_kernel_size, params_.morph_kernel_size)
  );
  
  // Opening (erosion followed by dilation) - removes small noise
  cv::morphologyEx(image, processed, cv::MORPH_OPEN, kernel, 
                   cv::Point(-1, -1), params_.morph_iterations);
  
  // Closing (dilation followed by erosion) - fills small holes
  cv::morphologyEx(processed, processed, cv::MORPH_CLOSE, kernel,
                   cv::Point(-1, -1), params_.morph_iterations);
  
  return processed;
}

cv::Mat ImageProcessor::create_color_mask(const cv::Mat& hsv_image, const ColorRange& color_range) const
{
  cv::Mat mask;
  cv::inRange(hsv_image, color_range.lower, color_range.upper, mask);
  return mask;
}

cv::Mat ImageProcessor::threshold(const cv::Mat& image) const
{
  cv::Mat binary;
  if (image.channels() == 3) {
    cv::cvtColor(image, binary, cv::COLOR_BGR2GRAY);
  } else {
    binary = image.clone();
  }
  
  cv::threshold(binary, binary, 0, 255, params_.threshold_type);
  return binary;
}

cv::Mat ImageProcessor::detect_edges(const cv::Mat& image, double low_threshold, double high_threshold) const
{
  cv::Mat gray, edges;
  
  if (image.channels() == 3) {
    cv::cvtColor(image, gray, cv::COLOR_BGR2GRAY);
  } else {
    gray = image;
  }
  
  cv::GaussianBlur(gray, gray, cv::Size(3, 3), 0);
  cv::Canny(gray, edges, low_threshold, high_threshold);
  
  return edges;
}

std::vector<std::vector<cv::Point>> ImageProcessor::find_contours(const cv::Mat& binary) const
{
  std::vector<std::vector<cv::Point>> contours;
  cv::findContours(binary, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);
  return contours;
}

std::vector<std::vector<cv::Point>> ImageProcessor::filter_contours(
  const std::vector<std::vector<cv::Point>>& contours) const
{
  std::vector<std::vector<cv::Point>> filtered;
  
  for (const auto& contour : contours) {
    double area = cv::contourArea(contour);
    
    // Filter by area
    if (area < params_.min_contour_area || area > params_.max_contour_area) {
      continue;
    }
    
    // Filter by circularity
    double circularity = calculate_circularity(contour);
    if (circularity < params_.min_circularity || circularity > params_.max_circularity) {
      continue;
    }
    
    filtered.push_back(contour);
  }
  
  return filtered;
}

DetectedObject ImageProcessor::contour_to_object(
  const std::vector<cv::Point>& contour,
  const cv::Mat& image) const
{
  DetectedObject obj;
  
  obj.bounding_box = cv::boundingRect(contour);
  obj.area = cv::contourArea(contour);
  obj.perimeter = cv::arcLength(contour, true);
  obj.circularity = calculate_circularity(contour);
  obj.moments = cv::moments(contour);
  obj.rotated_rect = cv::minAreaRect(contour);
  
  // Calculate center
  if (obj.moments.m00 != 0) {
    obj.center = cv::Point2f(
      static_cast<float>(obj.moments.m10 / obj.moments.m00),
      static_cast<float>(obj.moments.m01 / obj.moments.m00)
    );
  } else {
    obj.center = cv::Point2f(
      obj.bounding_box.x + obj.bounding_box.width / 2.0f,
      obj.bounding_box.y + obj.bounding_box.height / 2.0f
    );
  }
  
  // Get mean color
  cv::Mat mask = cv::Mat::zeros(image.size(), CV_8U);
  cv::drawContours(mask, std::vector<std::vector<cv::Point>>{contour}, 0, cv::Scalar(255), cv::FILLED);
  obj.mean_color = get_mean_color(image, mask);
  
  // Calculate confidence based on circularity and area
  obj.confidence = obj.circularity;
  
  return obj;
}

cv::Mat ImageProcessor::draw_detections(
  const cv::Mat& image,
  const std::vector<DetectedObject>& objects) const
{
  cv::Mat display = image.clone();
  
  for (const auto& obj : objects) {
    // Draw bounding box
    cv::rectangle(display, obj.bounding_box, cv::Scalar(0, 255, 0), 2);
    
    // Draw center
    cv::circle(display, obj.center, 5, cv::Scalar(0, 0, 255), -1);
    
    // Draw rotated rectangle
    cv::Point2f points[4];
    obj.rotated_rect.points(points);
    for (int i = 0; i < 4; ++i) {
      cv::line(display, points[i], points[(i + 1) % 4], cv::Scalar(255, 0, 0), 2);
    }
    
    // Draw label
    std::string label = obj.color_class + " (" + 
                        std::to_string(static_cast<int>(obj.confidence * 100)) + "%)";
    
    int baseline = 0;
    //cv::Size textSize = cv::getTextSize(label, cv::FONT_HERSHEY_SIMPLEX, 0.5, 1, &baseline);
    cv::Point textOrg(obj.bounding_box.x, obj.bounding_box.y - 5);
    
    cv::putText(display, label, textOrg, cv::FONT_HERSHEY_SIMPLEX, 0.5, 
                cv::Scalar(255, 255, 255), 1);
  }
  
  return display;
}

cv::Mat ImageProcessor::draw_color_masks(
  const cv::Mat& image,
  const std::map<std::string, cv::Mat>& masks) const
{
  cv::Mat overlay = image.clone();
  
  for (const auto& [name, mask] : masks) {
    // Find display color for this color name
    cv::Scalar color(255, 255, 255);
    auto it = std::find_if(params_.color_ranges.begin(), params_.color_ranges.end(),
      [&name](const ColorRange& r) { return r.name == name; });
    
    if (it != params_.color_ranges.end()) {
      color = it->display_color;
    }
    
    overlay.setTo(color, mask);
  }
  
  // Blend with original
  cv::Mat result;
  cv::addWeighted(image, 0.7, overlay, 0.3, 0, result);
  
  return result;
}

double ImageProcessor::calculate_circularity(const std::vector<cv::Point>& contour)
{
  double area = cv::contourArea(contour);
  double perimeter = cv::arcLength(contour, true);
  
  if (perimeter == 0) {
    return 0.0;
  }
  
  // Circularity = 4 * pi * area / perimeter^2
  // For a perfect circle, this equals 1.0
  return 4.0 * M_PI * area / (perimeter * perimeter);
}

cv::Scalar ImageProcessor::get_mean_color(const cv::Mat& image, const cv::Mat& mask)
{
  return cv::mean(image, mask);
}

void ImageProcessor::add_color_range(const ColorRange& color_range)
{
  // Remove existing range with same name
  params_.color_ranges.erase(
    std::remove_if(params_.color_ranges.begin(), params_.color_ranges.end(),
      [&color_range](const ColorRange& r) { return r.name == color_range.name; }),
    params_.color_ranges.end()
  );
  
  params_.color_ranges.push_back(color_range);
}

void ImageProcessor::clear_color_ranges()
{
  params_.color_ranges.clear();
}

}  // namespace lra_vision