#pragma once

#include "unordered_map"

#include "Event.h"

class DataHandler {
    public:
        virtual bool has_next() = 0;

        virtual std::unique_ptr<MarketEvent> next() = 0;

        void set_context(Context* context_);
};

class CustomUniverseDataHandler : public DataHandler {
    public:
        bool has_next();
        std::unique_ptr<MarketEvent> next();
};