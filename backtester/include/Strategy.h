#pragma once

#include "Event.h"

class Strategy {
    public:
        virtual ~Strategy();

        virtual void on_start();

        // Called on universe update, returns any signals
        virtual std::vector<std::shared_ptr<Signal>> on_update(std::shared_ptr<MarketEvent> event);
};