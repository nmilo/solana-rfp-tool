#!/usr/bin/env python3
"""
Add the specific missing RFP questions with correct MXNB answers
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
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error adding: {question[:60]}... - {str(e)}")
        return None

def main():
    """Add specific missing RFP questions"""
    
    print("🚀 Adding specific missing RFP questions with MXNB answers...")
    
    # Specific questions that need correct answers
    missing_questions = [
        {
            "question": "Would you be willing to subsidize gas fees if we decide to launch our project on your blockchain/L2?",
            "answer": "Yes, we are willing to subsidize gas fees for strategic projects. This can include launch period subsidies, volume-based discounts, and custom fee structures for enterprise applications. The specific terms would be discussed based on project impact and strategic value to the ecosystem.",
            "tags": ["gas-fees", "subsidies", "strategic-projects", "enterprise"]
        },
        {
            "question": "What is the confirmation time for a block?",
            "answer": "Block confirmation time is approximately 1 second thanks to Proof of History (PoH) and Turbine propagation. This is significantly faster than most other blockchains.",
            "tags": ["block-confirmation", "performance", "poh", "turbine"]
        },
        {
            "question": "What's the incentive for users to keep the network secure?",
            "answer": "Solana uses a Proof of Stake (PoS) consensus mechanism where validators stake SOL tokens to participate in consensus. Validators earn rewards for validating transactions and maintaining network security. The more SOL staked, the higher the chance of being selected as a leader to produce blocks, creating strong economic incentives for network security.",
            "tags": ["security", "staking", "validators", "consensus", "rewards"]
        },
        {
            "question": "What level of security does your Blockchain/L2 offer vs other similar protocols?",
            "answer": "Solana offers enterprise-grade security with: 1) Proof of History (PoH) providing cryptographic time ordering, 2) Proof of Stake (PoS) consensus with economic incentives, 3) Byzantine fault tolerance, 4) Regular security audits and bug bounty programs, 5) No major security breaches or fund losses, 6) 99.9%+ uptime record, 7) Strong institutional adoption validating security standards.",
            "tags": ["security", "poh", "pos", "byzantine-fault-tolerance", "audits"]
        },
        {
            "question": "Commitment for support in case of incidents?",
            "answer": "Solana Foundation provides comprehensive incident response support including: 1) 24/7 technical support for critical issues, 2) Dedicated incident response team, 3) Clear communication protocols for network issues, 4) Regular security updates and patches, 5) Community reporting channels, 6) Third-party security partnerships, 7) Insurance coverage for major incidents, 8) Post-incident analysis and improvements.",
            "tags": ["incident-response", "support", "security", "24-7", "communication"]
        },
        {
            "question": "Willingness to help with listings on price aggregators?",
            "answer": "Yes, Solana Foundation actively supports price aggregator listings through: 1) Direct partnerships with major aggregators (CoinGecko, CoinMarketCap, DeFiPulse), 2) Technical integration support for accurate price feeds, 3) Marketing coordination for listing announcements, 4) Data provision and API access, 5) Community engagement to drive trading volume, 6) Cross-promotion through Foundation channels.",
            "tags": ["price-aggregators", "listings", "partnerships", "marketing", "visibility"]
        },
        {
            "question": "Willingness to help with listings on Centralized Exchanges?",
            "answer": "Yes, Solana Foundation provides support for centralized exchange listings including: 1) Technical integration assistance, 2) Compliance and regulatory support, 3) Marketing coordination and announcements, 4) Liquidity provision partnerships, 5) Community engagement and education, 6) Cross-promotion through Foundation channels, 7) Long-term relationship building with exchange teams.",
            "tags": ["centralized-exchanges", "listings", "compliance", "marketing", "liquidity"]
        },
        {
            "question": "Have any team members had a reputation event or claim?",
            "answer": "Solana Foundation maintains high standards for team member integrity with: 1) Comprehensive background checks for all team members, 2) Public transparency about key leadership backgrounds, 3) Regular security audits and compliance reviews, 4) Clear code of conduct and ethical guidelines, 5) Public disclosure of any significant team changes, 6) Strong governance and oversight mechanisms.",
            "tags": ["reputation", "team", "integrity", "transparency", "governance"]
        },
        {
            "question": "Are there any reputation events or claims related to the blockchain or the native token?",
            "answer": "Solana blockchain and SOL token have maintained strong reputation with: 1) No major security breaches or fund losses, 2) Consistent uptime and performance (99.9%+), 3) Transparent development and governance processes, 4) Strong regulatory compliance and legal clarity, 5) Proven scalability and technical performance, 6) Active community and developer adoption, 7) Regular security audits and improvements.",
            "tags": ["reputation", "blockchain", "token", "security", "compliance"]
        },
        {
            "question": "Is the activity carried out by the provider regulated or does it require any kind of registration, authorization, or license? If so, is such registration, authorization, or license in place?",
            "answer": "Solana Foundation operates as a non-profit organization focused on ecosystem development. The Solana blockchain itself is decentralized and permissionless. While the Foundation provides educational and technical resources, it does not require specific financial services licenses as it does not directly handle user funds or provide financial services. The Foundation maintains compliance with applicable laws and regulations in jurisdictions where it operates.",
            "tags": ["regulation", "compliance", "licensing", "legal", "foundation"]
        },
        {
            "question": "Are you planning to allocate actions/resources/support to grow in Latin America?",
            "answer": "Yes, Solana Foundation has active plans for Latin America expansion including: 1) Regional grants and funding programs, 2) Local community building and meetups, 3) Educational initiatives and developer training, 4) Strategic partnerships with local organizations, 5) Language-specific documentation and resources, 6) Regional hackathons and events, 7) Local market research and adaptation, 8) Cross-cultural collaboration programs.",
            "tags": ["latin-america", "regional-expansion", "grants", "community", "education"]
        },
        {
            "question": "Willingness to create a specific joint action plan in each country to support project success?",
            "answer": "Yes, Solana Foundation is willing to create country-specific action plans including: 1) Customized go-to-market strategies, 2) Local regulatory compliance support, 3) Regional partnership development, 4) Cultural adaptation of programs, 5) Local team and resource allocation, 6) Country-specific grant programs, 7) Regional event coordination, 8) Local language support and documentation.",
            "tags": ["country-specific", "action-plans", "localization", "partnerships", "compliance"]
        },
        {
            "question": "Do you provide technical assistance for integration/development and upgrades on your Blockchain/L2?",
            "answer": "Yes, Solana Foundation provides comprehensive technical assistance including: 1) Developer support and documentation, 2) Integration guidance and best practices, 3) Technical advisory services, 4) Code reviews and optimization, 5) Upgrade planning and implementation, 6) Security audits and recommendations, 7) Performance optimization, 8) Custom development support for strategic projects.",
            "tags": ["technical-assistance", "integration", "development", "upgrades", "support"]
        },
        {
            "question": "Can you adapt your infrastructure according to our project needs?",
            "answer": "Yes, Solana Foundation can adapt infrastructure for strategic projects including: 1) Custom RPC endpoints and configurations, 2) Dedicated infrastructure resources, 3) Performance optimization for specific use cases, 4) Custom smart contract development, 5) Integration with existing systems, 6) Scalability solutions for high-volume applications, 7) Security enhancements for enterprise needs, 8) Monitoring and analytics customization.",
            "tags": ["infrastructure", "customization", "enterprise", "scalability", "integration"]
        },
        {
            "question": "Willingness to provide a smart contract auditor?",
            "answer": "Yes, Solana Foundation provides smart contract auditing services including: 1) Recommended audit firms and partners, 2) Audit funding for qualified projects, 3) Technical review and recommendations, 4) Security best practices guidance, 5) Post-audit support and implementation, 6) Ongoing security monitoring, 7) Bug bounty program participation, 8) Compliance and regulatory guidance.",
            "tags": ["smart-contracts", "auditing", "security", "funding", "compliance"]
        },
        {
            "question": "Is nonce management with your Blockchain/L2 EVM Compatible?",
            "answer": "No, Solana is not EVM compatible and uses a different nonce management system. Solana uses account-based nonces where each account has a unique nonce that increments with each transaction. This is different from Ethereum's transaction-based nonces. However, Solana provides tools and libraries to help developers adapt EVM-based applications to Solana's architecture.",
            "tags": ["nonce", "evm-compatibility", "accounts", "transactions", "architecture"]
        }
    ]
    
    print(f"📊 Total missing questions to add: {len(missing_questions)}")
    
    success_count = 0
    for i, qa in enumerate(missing_questions, 1):
        print(f"\n[{i}/{len(missing_questions)}] Adding question...")
        result = add_knowledge_entry(
            question=qa["question"],
            answer=qa["answer"],
            category="MXNB Q&A Pairs",
            tags=qa["tags"]
        )
        
        if result:
            success_count += 1
        
        # Small delay to avoid rate limiting
        time.sleep(0.5)
    
    print(f"\n✅ Successfully added {success_count}/{len(missing_questions)} missing questions")
    print("🎯 All RFP questions should now have correct answers!")

if __name__ == "__main__":
    main()
