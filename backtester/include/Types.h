#pragma once

#include <string>

enum class EventType {MARKET, SIGNAL, ORDER, FILL};
enum class Direction {SELL, BUY};
enum class OrderType {MARKET, LIMIT};

struct Bar {
    std::string ticker;
    long long timestamp;
    double open, high, low, close, volume;
};

struct Fill {
    std::string ticker;
    double quantity;
    double fill_price;
    double commission;
};

struct Order {
    OrderType order_type;
    std::string ticker;
    Direction direction;
    double quantity;
    double limit_price = 0;
};

struct Signal {
    std::string strategy_id;
    std::string ticker;
    double value;
};