#pragma once

#include <memory>

#include "Event.h"
#include "Context.h"

class ExecutionHandler {
    public:
        ExecutionHandler(double slippage = 0.0005, double commission = 0.35);

        void on_market_update(const MarketEvent& update); // Assumes limit orders don't carry over
        void submit_order(std::unique_ptr<Order> order);
        void set_context(Context context_);

    private:
        double slippage;
        double commission; // Price per share

        std::vector<std::unique_ptr<Order>> pending_orders;

        double calculate_commission(double quantity, double share_price);
        void execute_order(const Order& order, double share_price);

        Context context;
};