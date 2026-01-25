#pragma once

#include <memory>

#include "Event.h"

class ExecutionHandler {
    public:
        ExecutionHandler(double slippage = 0.0005, double commission = 0.35);

        std::vector<std::shared_ptr<Fill>> on_market_update(std::shared_ptr<MarketEvent> update); // Assumes limit orders don't carry over
        void submit_orders(const std::vector<std::shared_ptr<Order>>& orders);

    private:
        double slippage;
        double commission; // Price per share

        std::vector<std::shared_ptr<Order>> pending_orders;

        double calculate_commission(double quantity, double share_price);
        Fill execute_order(std::shared_ptr<Order> order, double share_price);
};