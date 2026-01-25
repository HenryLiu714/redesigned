cmake_minimum_required(VERSION 3.10)
project(backtester)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add the include directories
include_directories(${CMAKE_SOURCE_DIR}/backtester/include)

# Add source files
set(SOURCES
    backtester/src/Engine.cpp
    backtester/src/ExecutionHandler.cpp
)

# Create the main library
add_library(backtester_lib ${SOURCES})

# Find and link Google Test
find_package(GTest REQUIRED)

# Enable testing
enable_testing()

# Add test executable
add_executable(backtester_tests
    tests/ExecutionHandlerBehaviorTest.cpp
    tests/EngineTest.cpp
)

# Link the test executable with the library and Google Test
target_link_libraries(backtester_tests
    backtester_lib
    GTest::gtest
    GTest::gtest_main
)

# Register tests
add_test(NAME backtester_tests COMMAND backtester_tests)
