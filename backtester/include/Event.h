#pragma once

#include <string>
#include <vector>
#include <unordered_map>

#include "Types.h"

struct Event {
    virtual ~Event() = default;

    EventType type;
    long long timestamp;
};

// Notification of new data
struct MarketEvent : public Event {
    MarketEvent() {type = EventType::MARKET;}
    std::unordered_map<std::string, Bar> bars;
};

struct SignalEvent : public Event {
    SignalEvent() {type = EventType::SIGNAL;}
    std::string ticker;
    double value; // adjustable by strategy
    std::string strategy_id;

};

struct OrderEvent : public Event {
    OrderEvent() {type = EventType::ORDER;}
    std::shared_ptr<Order> order;
};

struct FillEvent : public Event {
    FillEvent() {type = EventType::FILL;}
    std::shared_ptr<Fill> fill;
};
