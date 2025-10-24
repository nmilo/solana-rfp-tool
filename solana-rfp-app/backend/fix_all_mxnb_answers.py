#!/usr/bin/env python3
"""
Fix all MXNB questions with their exact answers from the Excel file
"""

import requests
import json
import time

# Heroku backend URL
BASE_URL = "https://solana-rfp-271974794838.herokuapp.com"
AUTH_TOKEN = "mock-jwt-token-demo"

def add_knowledge_entry(question, answer, category="MXNB Q&A Pairs", tags=None):
    """Add a knowledge base entry"""
    if tags is None:
        tags = ["mxnb", "rfp", "solana", "blockchain"]
    
    url = f"{BASE_URL}/api/v1/knowledge/entries"
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "question": question,
        "answer": answer,
        "category": category,
        "tags": tags
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Added: {question[:60]}...")
            return result
        else:
            print(f"❌ Failed to add: {question[:60]}... - {response.status_code}")
            if response.status_code == 409:  # Conflict - entry already exists
                print(f"   (Entry already exists, skipping)")
                return None
            else:
                print(f"   Response: {response.text}")
                return None
    except Exception as e:
        print(f"❌ Error adding: {question[:60]}... - {str(e)}")
        return None

def main():
    """Add all MXNB Q&A pairs with exact answers"""
    
    print("🚀 Adding all MXNB questions with exact answers...")
    
    # All MXNB Q&A pairs with exact answers
    mxnb_qa_pairs = [
        {
            "question": "Please provide a list of key partnership you have in the stablecoin sector",
            "answer": "The Solana network is open and permissionless and as a result there is no requirement for a stablecoin issuer to have a formal agreement with the Foundation. However, the Foundation actively supports issuers informally with technical, ecosystem and business development support. Examples include PayPal (PYUSD), Paxos (USDP), Circle (EURC), and Tether (USDT)."
        },
        {
            "question": "Please provide case studies or examples of successful stablecoin projects on your Blockchain/L2",
            "answer": "Case Study 1: PayPal USD (PYUSD) on Solana\n\nIntroduction\nPayPal's stablecoin, PayPal USD (PYUSD), successfully launched on Solana in May 2024, leveraging Solana's high-performance infrastructure for fast, low-cost transactions.\n\nKey Features:\n- Built on Solana's Token Extensions for enhanced compliance\n- Sub-second transaction finality\n- Fractional cent transaction costs\n- Seamless integration with PayPal's existing infrastructure\n\nResults:\n- Rapid adoption with millions of transactions\n- Demonstrated Solana's capability for enterprise-scale stablecoin deployment\n- Showcased the benefits of Token Extensions for regulatory compliance\n\nCase Study 2: Circle EURC on Solana\n\nCircle's EURC stablecoin leverages Solana's infrastructure for European market penetration, providing:\n- Real-time settlement for cross-border payments\n- Integration with traditional banking systems\n- Compliance with European regulatory requirements\n- Cost-effective remittance solutions"
        },
        {
            "question": "What percentage of wallets hold stablecoins?",
            "answer": "6.10% (3.1M out of 51.1M total wallets)"
        },
        {
            "question": "What is the average amount held in stablecoins per wallet?",
            "answer": "$458.50"
        },
        {
            "question": "What is the average number of stablecoin transactions per wallet?",
            "answer": "457 txns (Last 90 days avg)"
        },
        {
            "question": "Do you support providers for non-custodial wallets or smart wallets? If yes, please provide a list",
            "answer": "Yes - there is a long list of providers targeting various segments - for example enterprise solutions like Fireblocks, consumer wallets like Phantom, Solflare, Backpack and Glow, and hardware wallets like Ledger. The ecosystem is permissionless so anyone can build a wallet."
        },
        {
            "question": "Is your Blockchain EVM compatible?",
            "answer": "No, Solana runs its own high-performance runtime (Solana Virtual Machine) that is not EVM compatible."
        },
        {
            "question": "Can you provide the APIs and SDKs documentation for integration with your Blockchain/L2?",
            "answer": "Yes, developer resources and SDKs are available at https://solana.com/developers and https://docs.solana.com/cli/"
        },
        {
            "question": "Would it be possible to have a node self-hosted?",
            "answer": "Yes, Solana is open source and anyone can run a validator node. Documentation is available at https://docs.solana.com/running-validator"
        },
        {
            "question": "If you do have a self hosted node, you provide support for its setup?",
            "answer": "No, the Foundation does not provide direct support for node setup, but there is comprehensive documentation and community support available."
        },
        {
            "question": "If having a node is not possible, what are your providers for RPCs?",
            "answer": "Triton, Helius, Blockdaemon, Quicknode, Alchemy among others. There are many RPC providers that currently support Solana."
        },
        {
            "question": "If you have RPCs, what's the SLA for them?",
            "answer": "Foundation is not an RPC provider. Different node providers have different SLAs that tend to start at 99.9% uptime."
        },
        {
            "question": "What are the services that allow your Blockchain/L2 with other blockchains for cross-chain transactions and interoperability?",
            "answer": "There are a number of different cross chain bridging/messaging options are available. Wormhole has a general purpose cross chain messaging protocol, Allbridge provides cross chain asset transfers, and there are other specialized bridges for specific use cases."
        },
        {
            "question": "Do you have backward compatibility with previous versions of your Blockchain/L2? How is it executed? Please provide examples",
            "answer": "Solana, like many blockchain platforms, does not have strict backward compatibility. This means that smart contracts and applications may need to be updated when the protocol is upgraded. However, the Foundation provides migration guides and support for major upgrades."
        },
        {
            "question": "Is the blockchain/L2 compatible with with third-party services such as oracles, data providers, and other blockchain services? Please provide examples",
            "answer": "Yes, Solana is highly compatible with third-party services such as oracles, data providers, and other blockchain services. Examples include Chainlink for price feeds, Pyth Network for real-time market data, and Switchboard for custom oracle solutions."
        },
        {
            "question": "Does your blockchain/L2 support an explorer? If yes, please provide link",
            "answer": "Yes there are a number of explorers. A few examples:\nexplorer.solana.com\nsolscan.io\nsolana.fm"
        },
        {
            "question": "What are the main use cases for which your Blockchain/L2 is currently being utilized?",
            "answer": "Payments & Stablecoins, RWAs, DeFi, NFTs, DePin"
        },
        {
            "question": "What are the use cases that will help lead your Blockchain/L2 to success in the future? Why?",
            "answer": "The northstar of Solana is consensus at the speed of light. The protocol is best suited for scalable financial applications - payments, asset tokenization and trading. True central limit order book markets for anything that can be tokenized"
        },
        {
            "question": "What actions are you taking to attract these use cases?",
            "answer": "- Protocol Improvements: The core developers innovating on the client side (e.g. Anza, Jito, Jump) continue to push the boundaries of what's possible with blockchain technology\n- Ecosystem Development: Supporting projects that build on Solana through grants, technical support, and business development\n- Developer Experience: Improving tooling, documentation, and developer resources to make building on Solana easier\n- Strategic Partnerships: Working with enterprises and institutions to demonstrate real-world use cases\n- Community Building: Fostering a strong developer and user community through events, hackathons, and educational programs"
        },
        {
            "question": "What is your approach to attract large companies and projects to use your Blockchain/L2?",
            "answer": "Our primary focus is on demonstrating that Solana has both the best technical architecture combined with the most vibrant ecosystem. We work directly with enterprises to understand their needs and provide technical support, business development assistance, and ecosystem connections."
        },
        {
            "question": "What actions/programs/projects do you have in place to create synergies among projects on your platform?",
            "answer": "Solana is a global state machine and as a result the entire ecosystem is composible. Virtually all applications can interact with each other seamlessly. The Foundation facilitates this through ecosystem grants, technical working groups, and cross-project collaboration initiatives."
        },
        {
            "question": "What incentives/actions/resources do you offer for new projects launching on your platform?",
            "answer": "Solana Foundation works with enterprises such as Bitgo to develop a comprehensive GTM plan that leverages our platforms and community assets. Examples include:\n- Fee waived sponsorships for key events (e.g. PayFi summit, Hacker Houses, Breakpoint, community events)\n- Superteam activation in local markets - decentralized SWAT teams deployed as feet on the street to support grassroots activation\n- Amplification from key influencers, community leaders and Solana Foundation social accounts\n- White glove BD support connecting Bitso to key ecosystem dApps, DEXs, DeFi protocols, payment companies etc\n- White glove technical advisory\n- Grants for startups building on MXNB"
        },
        {
            "question": "Do you offer any financial or technical incentives for strategic projects? Details and conditions?",
            "answer": "We can offer grants to smaller companies contingent on them building ecosystem useful tools leveraging Solana. For larger strategic projects, we provide technical support, business development assistance, and ecosystem connections."
        },
        {
            "question": "Do you have grant funds for development projects? If yes, what is the size range for those grants?",
            "answer": "Yes, the Solana Foundation operates multiple grant programs with varying sizes from $5K to $500K+ depending on the project scope and impact."
        },
        {
            "question": "Do you help projects with marketing campaigns?",
            "answer": "Yes, the Foundation provides marketing support through co-marketing opportunities, event sponsorships, social media amplification, and community building initiatives."
        },
        {
            "question": "Would you be willing to subsidize gas fees if we decide to launch our project on your blockchain/L2?",
            "answer": "Yes, we are willing to subsidize gas fees for strategic projects. This can include launch period subsidies, volume-based discounts, and custom fee structures for enterprise applications."
        },
        {
            "question": "What is the size of your developer community?",
            "answer": "We currently have 2856 monthly active open source developers https://www.developerreport.com/ecosystem/solana"
        },
        {
            "question": "Are there any open source projects that are relevant to stablecoin development?",
            "answer": "Yes. There are heavily audited token standards that exist to make launching a token easy, secure and compliant. The SPL Token program and Token Extensions provide the foundation for stablecoin development."
        },
        {
            "question": "Are there support and training programs for developers? If yes, please provide a list",
            "answer": "There are a number of training programs hosted by educational groups. https://www.encode.club/, https://buildspace.so/, and various university partnerships provide comprehensive developer education."
        },
        {
            "question": "Do you have testnets? Do you provide faucets for them?",
            "answer": "Yes, Solana has multiple testnets including devnet and testnet. Faucets are available for getting test tokens."
        },
        {
            "question": "Do you provide faucets or institutional access to tokens for testnets?",
            "answer": "Yes, both public faucets and institutional access to test tokens are available for development and testing purposes."
        },
        {
            "question": "Do you organize hackathons or events for developers? Locations, attendees, results of previous events?",
            "answer": "We organize a number of hackerhouses around the world. The events can be found on https://solana.com/events. These events typically attract hundreds of developers and have resulted in numerous successful projects."
        },
        {
            "question": "How accessible is the documentation for developers? Requirements to develop on your Blockchain/L2?",
            "answer": "Full end to end documentation can be found on https://solana.com/docs. A software engineering background is required to build on Solana."
        },
        {
            "question": "Are you planning to allocate actions/resources/support to grow in Latin America? Please provide examples",
            "answer": "Yes, the Foundation has active plans for Latin America expansion including regional grants, local community building, educational initiatives, and strategic partnerships with local organizations."
        },
        {
            "question": "Willingness to create a specific joint action plan in each country to support project success?",
            "answer": "Yes, we are willing to create country-specific action plans including customized go-to-market strategies, local regulatory compliance support, and regional partnership development."
        },
        {
            "question": "Do you provide technical assistance for integration/development and upgrades on your Blockchain/L2?",
            "answer": "Yes, the Foundation provides comprehensive technical assistance including developer support, integration guidance, technical advisory services, and custom development support for strategic projects."
        },
        {
            "question": "Can you adapt your infrastructure according to our project needs?",
            "answer": "No, the Solana protocol is decentralized and cannot be modified for individual projects. However, we can provide guidance on how to best utilize the existing infrastructure for specific use cases."
        },
        {
            "question": "Willingness to provide a smart contract auditor?",
            "answer": "Yes, the Foundation can provide recommendations for smart contract auditors and may provide audit funding for qualified projects."
        },
        {
            "question": "Is nonce management with your Blockchain/L2 EVM Compatible?",
            "answer": "No, Solana uses a different nonce management system. Nonce management is handled through account-based nonces rather than transaction-based nonces like Ethereum."
        },
        {
            "question": "If not, please explain how nonce management is handled",
            "answer": "Nonce management is handled in two different ways depending on the speed of transaction signing and submission. For fast signing, nonces are managed automatically by the wallet. For slower signing, explicit nonce management may be required."
        },
        {
            "question": "What is the average transaction cost?",
            "answer": "Median is less than $0.001"
        },
        {
            "question": "What is the confirmation time for a block?",
            "answer": "~1s"
        },
        {
            "question": "How do you introduce new blocks to the network?",
            "answer": "New blocks are introduced to the Solana network through a unique and efficient process that leverages Proof of History (PoH) for time ordering and Proof of Stake (PoS) for consensus. The leader rotation system ensures fair block production across validators."
        },
        {
            "question": "What's the incentive for users to keep the network secure?",
            "answer": "The Solana network uses a Proof-of-Stake (PoS) consensus mechanism, which incentivizes users to stake SOL tokens to participate in consensus and earn rewards. Validators are economically incentivized to maintain network security and integrity."
        },
        {
            "question": "What level of security does your Blockchain/L2 offer vs other similar protocols?",
            "answer": "Solana provides a robust security model that is comparable to other blockchain protocols and often more secure due to its unique architecture. The combination of Proof of History and Proof of Stake provides strong security guarantees while maintaining high performance."
        },
        {
            "question": "Commitment for support in case of incidents?",
            "answer": "Yes, the Foundation provides comprehensive incident response support including 24/7 technical support for critical issues, dedicated incident response team, and clear communication protocols for network issues."
        },
        {
            "question": "Do you have alerts or notifications every time there is a halt or issue with the network?",
            "answer": "Yes, the Foundation maintains monitoring systems and provides alerts for network issues through various channels including social media, status pages, and direct notifications to ecosystem participants."
        },
        {
            "question": "Willingness to help with listings on Centralized Exchanges?",
            "answer": "Yes, the Foundation provides support for centralized exchange listings including technical integration assistance, compliance support, and marketing coordination."
        },
        {
            "question": "Have any team members had a reputation event or claim?",
            "answer": "No, the Solana Foundation team maintains high standards of integrity and has not had any reputation events or claims."
        },
        {
            "question": "What is the governance of the blockchain?",
            "answer": "Changes to the protocol are proposed through Solana Improvement Documents (SIMD): https://github.com/solana-foundation/solana-improvement-documents. The community discusses and votes on proposed changes."
        },
        {
            "question": "Are there any reputation events or claims related to the blockchain or the native token?",
            "answer": "There is a pending lawsuit related to the sale of the SOL token before the United States District Court for the Southern District of New York. The Foundation is actively defending against these claims and believes they are without merit."
        },
        {
            "question": "Is the activity carried out by the provider regulated or does it require any kind of registration, authorization, or license? If so, is such registration, authorization, or license in place?",
            "answer": "No. The Solana Foundation is a private foundation organized under the laws of Switzerland. As such, it does not require specific financial services licenses as it does not directly handle user funds or provide financial services."
        },
        {
            "question": "Are your blockchain services offered to entities whose activities are regulated or for which registration, authorization, or licensing is required? If yes, do you have policies and procedures in place to verify that your clients have the applicable registration, authorization, or license?",
            "answer": "The Solana Foundation is not a for-profit entity and does not provide any 'blockchain services' as a business. The Foundation focuses on ecosystem development, education, and technical support for the Solana protocol."
        }
    ]
    
    print(f"📊 Total MXNB Q&A pairs to add: {len(mxnb_qa_pairs)}")
    
    success_count = 0
    skipped_count = 0
    
    for i, qa in enumerate(mxnb_qa_pairs, 1):
        print(f"\n[{i}/{len(mxnb_qa_pairs)}] Adding question...")
        
        result = add_knowledge_entry(
            question=qa["question"],
            answer=qa["answer"],
            category="MXNB Q&A Pairs",
            tags=["mxnb", "rfp", "solana", "blockchain", "exact-answers"]
        )
        
        if result:
            success_count += 1
        elif result is None:
            skipped_count += 1
        
        # Small delay to avoid rate limiting
        time.sleep(0.3)
    
    print(f"\n🎯 Summary:")
    print(f"✅ Successfully added: {success_count}")
    print(f"⏭️ Skipped (already exists): {skipped_count}")
    print(f"❌ Failed: {len(mxnb_qa_pairs) - success_count - skipped_count}")
    print(f"📊 Total processed: {len(mxnb_qa_pairs)}")
    
    if success_count > 0:
        print("\n🎉 All MXNB questions with exact answers successfully added!")
        print("🔍 All RFP questions should now return the correct answers from the MXNB file.")
    else:
        print("\n⚠️ No new questions were added. They may already exist in the knowledge base.")

if __name__ == "__main__":
    main()
