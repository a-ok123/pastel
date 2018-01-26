// Copyright (c) 2018 airk42
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef CONNMAN_H
#define CONNMAN_H

#include <string>
#include <vector>

#include "chainparams.h"
#include "protocol.h"
#include "net.h"

class CConnman 
{
public:
/***** MasterNode operations *****/
    static void ThreadMnbRequestConnections();

/***** vNodes vector operations *****/
    std::vector<CNode*> CopyNodeVector()
    {
        std::vector<CNode*> vecNodesCopy;
        LOCK(cs_vNodes);
        for(size_t i = 0; i < vNodes.size(); ++i) {
            CNode* pnode = vNodes[i];
            pnode->AddRef();
            vecNodesCopy.push_back(pnode);
        }
        return vecNodesCopy;
    }

    void ReleaseNodeVector(const std::vector<CNode*>& vecNodes)
    {
        LOCK(cs_vNodes);
        for(size_t i = 0; i < vecNodes.size(); ++i) {
            CNode* pnode = vecNodes[i];
            pnode->Release();
        }
    }

/***** vNodes itterators *****/
    template<typename Condition, typename Callable>
    bool ForEachNodeContinueIf(const Condition& cond, Callable&& func)
    {
        LOCK(cs_vNodes);
        for (auto&& node : vNodes)
            if (cond(node))
                if(!func(node))
                    return false;
        return true;
    };

    template<typename Callable>
    bool ForEachNodeContinueIf(Callable&& func)
    {
        return ForEachNodeContinueIf(FullyConnectedOnly, func);
    }

    template<typename Condition, typename Callable>
    bool ForEachNodeContinueIf(const Condition& cond, Callable&& func) const
    {
        LOCK(cs_vNodes);
        for (const auto& node : vNodes)
            if (cond(node))
                if(!func(node))
                    return false;
        return true;
    };

    template<typename Callable>
    bool ForEachNodeContinueIf(Callable&& func) const
    {
        return ForEachNodeContinueIf(FullyConnectedOnly, func);
    }


    template<typename Condition, typename Callable>
    void ForEachNode(const Condition& cond, Callable&& func)
    {
        LOCK(cs_vNodes);
        for (auto&& node : vNodes) {
            if (cond(node))
                func(node);
        }
    };

    template<typename Callable>
    void ForEachNode(Callable&& func)
    {
        ForEachNode(FullyConnectedOnly, func);
    }

    template<typename Condition, typename Callable>
    void ForEachNode(const Condition& cond, Callable&& func) const
    {
        LOCK(cs_vNodes);
        for (auto&& node : vNodes) {
            if (cond(node))
                func(node);
        }
    };

    template<typename Callable>
    void ForEachNode(Callable&& func) const
    {
        ForEachNode(FullyConnectedOnly, func);
    }

    template<typename Condition, typename Callable, typename CallableAfter>
    void ForEachNodeThen(const Condition& cond, Callable&& pre, CallableAfter&& post)
    {
        LOCK(cs_vNodes);
        for (auto&& node : vNodes) {
            if (cond(node))
                pre(node);
        }
        post();
    };

    template<typename Callable, typename CallableAfter>
    void ForEachNodeThen(Callable&& pre, CallableAfter&& post)
    {
        ForEachNodeThen(FullyConnectedOnly, pre, post);
    }

    template<typename Condition, typename Callable, typename CallableAfter>
    void ForEachNodeThen(const Condition& cond, Callable&& pre, CallableAfter&& post) const
    {
        LOCK(cs_vNodes);
        for (auto&& node : vNodes) {
            if (cond(node))
                pre(node);
        }
        post();
    };

    template<typename Callable, typename CallableAfter>
    void ForEachNodeThen(Callable&& pre, CallableAfter&& post) const
    {
        ForEachNodeThen(FullyConnectedOnly, pre, post);
    }

/***** Push message helpers *****/
    void RelayInv(CInv &inv, const int minProtoVersion = MIN_PEER_PROTO_VERSION) {
        LOCK(cs_vNodes);
        BOOST_FOREACH(CNode* pnode, vNodes)
            if(pnode->nVersion >= minProtoVersion)
                pnode->PushInventory(inv);
    }

/*****  *****/
    static bool NodeFullyConnected(const CNode* pnode)
    {
        return pnode && pnode->fSuccessfullyConnected && !pnode->fDisconnect;
    }

    struct CFullyConnectedOnly {
        bool operator() (const CNode* pnode) const {
            return NodeFullyConnected(pnode);
        }
    };
    constexpr static const CFullyConnectedOnly FullyConnectedOnly{};

    struct CAllNodes {
        bool operator() (const CNode*) const {return true;}
    };

    constexpr static const CAllNodes AllNodes{};
};

#endif
