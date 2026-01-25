#pragma once

#include "unordered_map"

#include "Event.h"

class DataHandler {
    public:
        virtual bool has_next() = 0;

        virtual std::shared_ptr<MarketEvent> next() = 0;
};

class CustomUniverseDataHandler : public DataHandler {
    public:
        bool has_next();
        std::shared_ptr<MarketEvent> next();
};