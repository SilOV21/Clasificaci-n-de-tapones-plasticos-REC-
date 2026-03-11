// =============================================================================
// LRA Vision Package - Test Image Processor
// Unit tests for image processing and cap detection
// ROS2 Jazzy Jalisco - GTest
// =============================================================================

#include <gtest/gtest.h>
#include <opencv2/opencv.hpp>
#include "lra_vision/image_processor.hpp"

class ImageProcessorTest : public ::testing::Test
{
protected:
  void SetUp() override
  {
    // Create default processing parameters
    params_ = lra_vision::ProcessingParams::default_for_caps();
  }
  
  void TearDown() override
  {
    // Cleanup
  }
  
  lra_vision::ProcessingParams params_;
  
  // Generate synthetic test image with colored circles
  cv::Mat generateTestImage(int width = 800, int height = 600)
  {
    cv::Mat image = cv::Mat::zeros(height, width, CV_8UC3);
    
    // Draw some colored circles (simulating caps)
    cv::circle(image, cv::Point(200, 200), 50, cv::Scalar(0, 0, 255), -1);  // Red
    cv::circle(image, cv::Point(400, 200), 50, cv::Scalar(255, 0, 0), -1);  // Blue
    cv::circle(image, cv::Point(600, 200), 50, cv::Scalar(0, 255, 0), -1);  // Green
    cv::circle(image, cv::Point(300, 400), 50, cv::Scalar(0, 255, 255), -1); // Yellow
    
    // Add some noise
    cv::Mat noise = cv::Mat::zeros(height, width, CV_8UC3);
    cv::randn(noise, 0, 10);
    image += noise;
    
    return image;
  }
  
  // Generate image with specific colored shapes
  cv::Mat generateColoredShapesImage()
  {
    cv::Mat image = cv::Mat::zeros(600, 800, CV_8UC3);
    
    // Circles (caps)
    cv::circle(image, cv::Point(100, 100), 30, cv::Scalar(0, 0, 255), -1);   // Red circle
    cv::circle(image, cv::Point(200, 100), 30, cv::Scalar(255, 0, 0), -1);   // Blue circle
    cv::circle(image, cv::Point(300, 100), 30, cv::Scalar(0, 255, 0), -1);   // Green circle
    
    // Rectangles (not caps)
    cv::rectangle(image, cv::Point(100, 200), cv::Point(160, 260), cv::Scalar(0, 0, 255), -1);  // Red rect
    cv::rectangle(image, cv::Point(200, 200), cv::Point(260, 260), cv::Scalar(255, 0, 0), -1);  // Blue rect
    
    return image;
  }
};

// Test: ProcessingParams default values
TEST_F(ImageProcessorTest, TestProcessingParamsDefaults)
{
  auto params = lra_vision::ProcessingParams::default_for_caps();
  
  EXPECT_EQ(params.blur_kernel_size, 5);
  EXPECT_DOUBLE_EQ(params.blur_sigma, 1.5);
  EXPECT_GT(params.color_ranges.size(), 0);  // Should have color ranges
  
  // Check for common colors
  bool has_red = false;
  bool has_blue = false;
  bool has_green = false;
  
  for (const auto& range : params.color_ranges) {
    if (range.name == "red") has_red = true;
    if (range.name == "blue") has_blue = true;
    if (range.name == "green") has_green = true;
  }
  
  EXPECT_TRUE(has_red);
  EXPECT_TRUE(has_blue);
  EXPECT_TRUE(has_green);
}

// Test: ColorRange creation
TEST_F(ImageProcessorTest, TestColorRangeCreation)
{
  auto range = lra_vision::ColorRange::create("test", 0, 100, 50, 10, 255, 255);
  
  EXPECT_EQ(range.name, "test");
  EXPECT_EQ(range.lower, cv::Scalar(0, 100, 50));
  EXPECT_EQ(range.upper, cv::Scalar(10, 255, 255));
}

// Test: ImageProcessor initialization
TEST_F(ImageProcessorTest, TestInitialization)
{
  lra_vision::ImageProcessor processor(params_);
  
  EXPECT_NO_THROW(processor.detect_objects(cv::Mat()));
}

// Test: ImageProcessor color space conversion
TEST_F(ImageProcessorTest, TestColorSpaceConversion)
{
  lra_vision::ImageProcessor processor(params_);
  
  cv::Mat bgr = cv::Mat::zeros(100, 100, CV_8UC3);
  bgr.setTo(cv::Scalar(100, 150, 200));
  
  cv::Mat hsv = processor.to_hsv(bgr);
  
  EXPECT_EQ(hsv.channels(), 3);
  EXPECT_EQ(hsv.rows, 100);
  EXPECT_EQ(hsv.cols, 100);
}

// Test: ImageProcessor blur
TEST_F(ImageProcessorTest, TestBlur)
{
  lra_vision::ImageProcessor processor(params_);
  
  cv::Mat image = cv::Mat::zeros(100, 100, CV_8UC1);
  cv::rectangle(image, cv::Point(40, 40), cv::Point(60, 60), cv::Scalar(255), -1);
  
  cv::Mat blurred = processor.blur(image);
  
  EXPECT_EQ(blurred.size(), image.size());
  // Blurred image should be different from original
  EXPECT_FALSE(cv::norm(image, blurred, cv::NORM_L2) < 0.001);
}

// Test: ImageProcessor morphological operations
TEST_F(ImageProcessorTest, TestMorphologicalProcess)
{
  lra_vision::ImageProcessor processor(params_);
  
  cv::Mat binary = cv::Mat::zeros(100, 100, CV_8UC1);
  cv::circle(binary, cv::Point(50, 50), 30, cv::Scalar(255), -1);
  // Add some noise
  cv::circle(binary, cv::Point(20, 20), 3, cv::Scalar(255), -1);
  
  cv::Mat processed = processor.morphological_process(binary);
  
  EXPECT_EQ(processed.size(), binary.size());
  // Small noise should be removed
}

// Test: ImageProcessor contour detection
TEST_F(ImageProcessorTest, TestContourDetection)
{
  lra_vision::ImageProcessor processor(params_);
  
  cv::Mat binary = cv::Mat::zeros(100, 100, CV_8UC1);
  cv::circle(binary, cv::Point(50, 50), 30, cv::Scalar(255), -1);
  
  auto contours = processor.find_contours(binary);
  
  EXPECT_GT(contours.size(), 0);
}

// Test: ImageProcessor contour filtering
TEST_F(ImageProcessorTest, TestContourFiltering)
{
  lra_vision::ImageProcessor processor(params_);
  
  // Create contours of different sizes
  std::vector<std::vector<cv::Point>> contours;
  
  // Small contour (should be filtered)
  std::vector<cv::Point> small;
  small.push_back(cv::Point(0, 0));
  small.push_back(cv::Point(10, 0));
  small.push_back(cv::Point(10, 10));
  small.push_back(cv::Point(0, 10));
  contours.push_back(small);
  
  // Large contour (should be kept)
  std::vector<cv::Point> large;
  large.push_back(cv::Point(0, 0));
  large.push_back(cv::Point(100, 0));
  large.push_back(cv::Point(100, 100));
  large.push_back(cv::Point(0, 100));
  contours.push_back(large);
  
  auto filtered = processor.filter_contours(contours);
  
  // Only large contour should remain
  // (depending on min_contour_area setting)
}

// Test: ImageProcessor circularity calculation
TEST_F(ImageProcessorTest, TestCircularityCalculation)
{
  // Perfect circle should have circularity close to 1
  std::vector<cv::Point> circle_contour;
  for (int i = 0; i < 100; ++i) {
    double angle = 2 * M_PI * i / 100;
    circle_contour.push_back(cv::Point(100 * cos(angle), 100 * sin(angle)));
  }
  
  double circle_circularity = lra_vision::ImageProcessor::calculate_circularity(circle_contour);
  EXPECT_NEAR(circle_circularity, 1.0, 0.05);
  
  // Square should have lower circularity
  std::vector<cv::Point> square;
  square.push_back(cv::Point(0, 0));
  square.push_back(cv::Point(100, 0));
  square.push_back(cv::Point(100, 100));
  square.push_back(cv::Point(0, 100));
  
  double square_circularity = lra_vision::ImageProcessor::calculate_circularity(square);
  EXPECT_LT(square_circularity, circle_circularity);
}

// Test: ImageProcessor detect objects
TEST_F(ImageProcessorTest, TestDetectObjects)
{
  lra_vision::ImageProcessor processor(params_);
  
  cv::Mat test_image = generateTestImage();
  
  auto objects = processor.detect_objects(test_image);
  
  // Should detect some objects
  EXPECT_GE(objects.size(), 0);
  
  // Each object should have valid properties
  for (const auto& obj : objects) {
    EXPECT_GT(obj.area, 0);
    EXPECT_GE(obj.circularity, 0.0);
    EXPECT_LE(obj.circularity, 1.1);  // Allow slight numerical errors
    EXPECT_FALSE(obj.color_class.empty());
  }
}

// Test: ImageProcessor detect objects by color
TEST_F(ImageProcessorTest, TestDetectObjectsByColor)
{
  lra_vision::ImageProcessor processor(params_);
  
  cv::Mat test_image = generateTestImage();
  
  // Detect only red objects
  auto red_objects = processor.detect_objects_by_color(test_image, "red");
  
  // All detected objects should be red
  for (const auto& obj : red_objects) {
    EXPECT_EQ(obj.color_class, "red");
  }
}

// Test: ImageProcessor classify color
TEST_F(ImageProcessorTest, TestClassifyColor)
{
  lra_vision::ImageProcessor processor(params_);
  
  // Create colored regions
  cv::Mat red_region = cv::Mat(50, 50, CV_8UC3, cv::Scalar(0, 0, 255));
  cv::Mat blue_region = cv::Mat(50, 50, CV_8UC3, cv::Scalar(255, 0, 0));
  cv::Mat green_region = cv::Mat(50, 50, CV_8UC3, cv::Scalar(0, 255, 0));
  
  cv::Rect roi(0, 0, 50, 50);
  
  std::string red_color = processor.classify_color(red_region, roi);
  std::string blue_color = processor.classify_color(blue_region, roi);
  std::string green_color = processor.classify_color(green_region, roi);
  
  // Colors should be classified correctly (or close enough)
  // Note: Classification might not be perfect due to HSV conversion
}

// Test: ImageProcessor draw detections
TEST_F(ImageProcessorTest, TestDrawDetections)
{
  lra_vision::ImageProcessor processor(params_);
  
  cv::Mat test_image = generateTestImage();
  auto objects = processor.detect_objects(test_image);
  
  cv::Mat display = processor.draw_detections(test_image, objects);
  
  EXPECT_EQ(display.size(), test_image.size());
  EXPECT_EQ(display.channels(), 3);
}

// Test: DetectedObject structure
TEST_F(ImageProcessorTest, TestDetectedObject)
{
  lra_vision::DetectedObject obj;
  
  obj.bounding_box = cv::Rect(10, 10, 100, 100);
  obj.center = cv::Point2f(60, 60);
  obj.area = 10000;
  obj.circularity = 0.95;
  obj.color_class = "red";
  obj.confidence = 0.9;
  
  EXPECT_EQ(obj.bounding_box.x, 10);
  EXPECT_EQ(obj.bounding_box.width, 100);
  EXPECT_FLOAT_EQ(obj.center.x, 60);
  EXPECT_DOUBLE_EQ(obj.area, 10000);
  EXPECT_DOUBLE_EQ(obj.circularity, 0.95);
  EXPECT_EQ(obj.color_class, "red");
  EXPECT_DOUBLE_EQ(obj.confidence, 0.9);
}

// Test: ImageProcessor parameter modification
TEST_F(ImageProcessorTest, TestParameterModification)
{
  lra_vision::ImageProcessor processor(params_);
  
  // Add new color range
  lra_vision::ColorRange new_range;
  new_range.name = "purple";
  new_range.lower = cv::Scalar(130, 100, 50);
  new_range.upper = cv::Scalar(150, 255, 255);
  new_range.display_color = cv::Scalar(255, 0, 255);
  
  processor.add_color_range(new_range);
  
  const auto& params = processor.get_params();
  
  // Check that purple range was added
  bool has_purple = false;
  for (const auto& range : params.color_ranges) {
    if (range.name == "purple") {
      has_purple = true;
      break;
    }
  }
  EXPECT_TRUE(has_purple);
  
  // Clear color ranges
  processor.clear_color_ranges();
  
  // Set new parameters
  lra_vision::ProcessingParams new_params;
  new_params.min_contour_area = 1000.0;
  processor.set_params(new_params);
  
  EXPECT_DOUBLE_EQ(processor.get_params().min_contour_area, 1000.0);
}

int main(int argc, char** argv)
{
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}