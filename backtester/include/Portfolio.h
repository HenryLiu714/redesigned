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
        virtual void on_signal(const Signal& signal);
        virtual void on_fill(const Fill& fill);
        void send_order(std::unique_ptr<Order> order);
        void set_context(Context* context_);

    protected:
        double cash;
        std::unordered_map<std::string, double> active_positions;
};