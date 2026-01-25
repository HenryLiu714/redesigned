#pragma once

#include <unordered_map>

#include "Event.h"

struct Position {
    std::string ticker;
    int quantity;
    double entry_price;
    double current_price;
    long long entry_timestamp;
};

class Portfolio {
    public:
        virtual ~Portfolio();
        virtual void on_signals(const std::vector<std::shared_ptr<Signal>>& signals);
        virtual void on_fills(const std::vector<std::shared_ptr<Fill>>& fills);
        virtual std::vector<std::shared_ptr<Order>> send_orders();

    protected:
        double cash;
        std::unordered_map<std::string, double> active_positions;
        std::vector<std::shared_ptr<Fill>> queued_orders;
};