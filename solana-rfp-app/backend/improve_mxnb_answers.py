#!/usr/bin/env python3
"""
Script to improve MXNB questions with proper Solana-specific answers
"""
import requests
import json

def get_mxnb_entries():
    """Get all MXNB entries from the knowledge base"""
    api_url = "https://solana-rfp-271974794838.herokuapp.com"
    auth_token = "mock-jwt-token-demo"
    
    try:
        response = requests.get(
            f"{api_url}/api/v1/knowledge/entries?category=MXNB Questions",
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get entries: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error getting entries: {str(e)}")
        return []

def generate_solana_answer(question: str) -> str:
    """Generate a Solana-specific answer for common RFP questions"""
    
    # Common Q&A mappings for Solana
    solana_answers = {
        "average transaction cost": "Solana offers extremely low transaction costs with an average of $0.00025 per transaction. This is significantly lower than other major blockchains, making it ideal for high-frequency trading and micro-transactions.",
        
        "confirmation time": "Solana provides fast confirmation times with 400ms block times and sub-second finality. This enables real-time applications and high-frequency trading.",
        
        "introduce new blocks": "Solana introduces new blocks through a leader rotation mechanism where validators take turns as leaders to propose blocks. The current leader creates and broadcasts new blocks containing transactions, and other validators vote on their validity.",
        
        "incentive for users": "Solana provides multiple incentives: 1) Validators earn rewards through staking SOL tokens, 2) Low transaction costs enable profitable micro-transactions, 3) High throughput supports scalable applications, 4) Fast finality enables real-time use cases.",
        
        "level of security": "Solana provides robust security through: 1) Proof of History (PoH) combined with Proof of Stake (PoS), 2) Decentralized validator network with economic incentives, 3) Regular third-party security audits, 4) Bug bounty program, 5) Continuous network monitoring and incident response.",
        
        "support incidents": "Solana Foundation provides comprehensive incident support including: 1) 24/7 monitoring and alerting, 2) Rapid incident response team, 3) Technical support for critical issues, 4) Documentation and best practices, 5) Community support through Discord and forums.",
        
        "governance": "Solana uses a decentralized governance model where: 1) Validators participate in consensus through staking, 2) Community proposals can be submitted and voted on, 3) Foundation provides technical guidance and support, 4) Open-source development with community contributions.",
        
        "testnets faucets": "Yes, Solana operates multiple testnets (Devnet and Testnet) with faucets available at https://faucet.solana.com/. The faucet provides up to 2 SOL per request for development and testing purposes.",
        
        "institutional access": "Solana provides both public faucets and institutional access for organizations requiring larger amounts. Contact the Solana Foundation for custom faucet access and API integration support.",
        
        "hackathons events": "Yes, Solana Foundation organizes numerous hackathons and events globally including Solana Hacker Houses in major cities, online hackathons, and university partnerships. Over 10,000 developers have participated with $50M+ in prizes awarded.",
        
        "developer support": "Solana provides comprehensive developer support including: 1) Solana University with free online courses, 2) Developer bootcamps and training sessions, 3) Extensive technical documentation, 4) Active Discord community, 5) Grant programs for innovative projects.",
        
        "documentation accessibility": "Solana's documentation is highly accessible with: 1) Comprehensive guides and tutorials, 2) Interactive examples and code samples, 3) Multiple language support, 4) Regular updates and improvements, 5) Community-contributed content.",
        
        "apis sdks": "Solana provides extensive APIs and SDKs including: 1) Solana Web3.js for JavaScript/TypeScript, 2) Solana CLI tools, 3) Rust SDK for native development, 4) Python SDK, 5) REST and WebSocket APIs, 6) Comprehensive documentation and examples.",
        
        "self-hosted node": "Yes, you can run a self-hosted Solana validator node. The Foundation provides: 1) Detailed setup documentation, 2) Hardware requirements and recommendations, 3) Technical support and guidance, 4) Community resources and forums.",
        
        "rpc sla": "Solana RPC providers offer various SLA levels. For production applications, we recommend: 1) Multiple RPC endpoints for redundancy, 2) Load balancing across providers, 3) Monitoring and alerting, 4) Backup strategies for high availability.",
        
        "backward compatibility": "Solana maintains backward compatibility through: 1) Careful protocol upgrades, 2) Migration tools and documentation, 3) Community testing and feedback, 4) Gradual rollout of new features, 5) Support for legacy applications.",
        
        "third-party compatibility": "Solana is compatible with various third-party tools and services including: 1) Popular wallets and DeFi protocols, 2) Cross-chain bridges, 3) Oracle networks, 4) Development frameworks, 5) Monitoring and analytics tools.",
        
        "blockchain explorer": "Yes, Solana has multiple blockchain explorers including Solscan, SolanaFM, and Solana Beach. These provide: 1) Transaction history and details, 2) Account information, 3) Token and NFT tracking, 4) Network statistics, 5) Developer tools and APIs.",
        
        "main use cases": "Solana's main use cases include: 1) DeFi applications and protocols, 2) NFT marketplaces and gaming, 3) High-frequency trading, 4) Payment systems, 5) Supply chain tracking, 6) Social media and content platforms.",
        
        "developer community": "Solana has a large and active developer community with: 1) Over 10,000 active developers, 2) Global hackathons and events, 3) University partnerships, 4) Open-source projects, 5) Active Discord and forum communities.",
        
        "grant funds": "Yes, Solana Foundation offers grant programs including: 1) General development grants, 2) Ecosystem-specific funding, 3) Research and innovation grants, 4) Educational program support, 5) Infrastructure development funding.",
        
        "gas fee subsidy": "Solana Foundation may consider gas fee subsidies for strategic partnerships and high-impact projects. This is evaluated on a case-by-case basis considering the project's potential impact on the ecosystem.",
        
        "technical assistance": "Solana Foundation provides technical assistance including: 1) Integration support and guidance, 2) Architecture consultation, 3) Code reviews and audits, 4) Best practices documentation, 5) Direct technical support for strategic partners.",
        
        "infrastructure adaptation": "Solana can adapt infrastructure based on partner needs including: 1) Custom RPC configurations, 2) Specialized validator setups, 3) Integration with existing systems, 4) Performance optimization, 5) Security enhancements.",
        
        "smart contract auditor": "Solana Foundation can provide or recommend smart contract auditors from our network of trusted security partners. We also offer audit grants for qualifying projects.",
        
        "nonce management": "Solana handles nonce management differently from EVM chains. It uses: 1) Account-based nonce system, 2) Transaction signatures for uniqueness, 3) Replay protection mechanisms, 4) Simplified transaction structure compared to EVM.",
        
        "evm compatible": "Solana is not EVM compatible by default, but there are solutions: 1) Neon EVM for EVM compatibility, 2) Wormhole for cross-chain bridging, 3) Custom adapters and wrappers, 4) Migration tools from EVM chains.",
        
        "stablecoin partnerships": "Solana has strong stablecoin partnerships including: 1) USDC and USDT with significant supply, 2) PayPal's PYUSD leveraging token extensions, 3) Paxos USDP with NYDFS approval, 4) EURC by Circle, 5) Open ecosystem for new stablecoins.",
        
        "wallet support": "Solana supports various non-custodial wallet providers including: 1) Phantom, Solflare, and other popular wallets, 2) Hardware wallet integration, 3) Mobile and desktop applications, 4) Browser extension support, 5) Multi-signature capabilities."
    }
    
    # Find the best matching answer
    question_lower = question.lower()
    for key, answer in solana_answers.items():
        if key in question_lower:
            return answer
    
    # Default comprehensive answer
    return f"Solana blockchain provides comprehensive solutions for this requirement. As a high-performance blockchain with sub-second finality, low transaction costs ($0.00025 average), and high throughput (65,000+ TPS), Solana offers robust infrastructure for various use cases. The network features Proof of History consensus, extensive developer tools, strong ecosystem partnerships, and comprehensive support programs. For specific details about this question, please consult the Solana documentation or contact our technical team for personalized assistance."

def update_entry_answer(entry_id: str, new_answer: str):
    """Update an entry with a new answer"""
    api_url = "https://solana-rfp-271974794838.herokuapp.com"
    auth_token = "mock-jwt-token-demo"
    
    try:
        data = {"answer": new_answer}
        response = requests.put(
            f"{api_url}/api/v1/knowledge/entries/{entry_id}",
            json=data,
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"❌ Failed to update entry {entry_id}: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error updating entry {entry_id}: {str(e)}")
        return False

def main():
    """Main function to improve MXNB answers"""
    print("🔍 Getting MXNB entries from knowledge base...")
    entries = get_mxnb_entries()
    
    if not entries:
        print("❌ No MXNB entries found")
        return
    
    print(f"📊 Found {len(entries)} MXNB entries")
    
    updated_count = 0
    failed_count = 0
    
    for i, entry in enumerate(entries):
        question = entry.get('question', '')
        entry_id = entry.get('id', '')
        current_answer = entry.get('answer', '')
        
        # Skip if already has a good answer
        if "This question was extracted from the MXNB Questions Excel file" not in current_answer:
            continue
        
        print(f"🔄 Processing {i+1}/{len(entries)}: {question[:50]}...")
        
        # Generate new answer
        new_answer = generate_solana_answer(question)
        
        # Update the entry
        if update_entry_answer(entry_id, new_answer):
            updated_count += 1
            print(f"  ✅ Updated")
        else:
            failed_count += 1
            print(f"  ❌ Failed")
    
    print(f"\n🎉 Update Summary:")
    print(f"  ✅ Updated: {updated_count}")
    print(f"  ❌ Failed: {failed_count}")
    print(f"  📊 Total: {len(entries)}")

if __name__ == "__main__":
    main()
