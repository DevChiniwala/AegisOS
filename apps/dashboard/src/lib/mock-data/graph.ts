import type { GraphData, Community } from "@/types/graph";

export const mockGraphData: GraphData = {
  nodes: [
    { id: "usr_8d2f1", type: "user", label: "Viktor Petrov", risk_score: 0.94, properties: { country: "RO", account_age: 12 } },
    { id: "usr_3a9c2", type: "user", label: "Maria Santos", risk_score: 0.89, properties: { country: "BR", account_age: 45 } },
    { id: "usr_mule_1", type: "user", label: "Account #4421", risk_score: 0.91, properties: { country: "NG" } },
    { id: "usr_mule_2", type: "user", label: "Account #7832", risk_score: 0.88, properties: { country: "GH" } },
    { id: "usr_mule_3", type: "user", label: "Account #1155", risk_score: 0.85, properties: { country: "KE" } },
    { id: "mrc_electronics", type: "merchant", label: "ElectroShop Pro", risk_score: 0.72, properties: { category: "electronics", mcc: "5732" } },
    { id: "mrc_fx_broker", type: "merchant", label: "QuickSwap FX", risk_score: 0.87, properties: { category: "crypto_exchange", mcc: "6051" } },
    { id: "dev_iphone15_x1", type: "device", label: "iPhone 15 Pro", risk_score: 0.65, properties: { os: "iOS 19", shared_users: 4 } },
    { id: "dev_pixel8_new", type: "device", label: "Pixel 8", risk_score: 0.45, properties: { os: "Android 16" } },
    { id: "ip_185_234", type: "ip", label: "185.234.12.44", risk_score: 0.78, properties: { country: "RO", is_vpn: true } },
    { id: "card_visa_ending_4421", type: "card", label: "Visa *4421", risk_score: 0.82, properties: { issuer: "Chase" } },
    { id: "usr_regular_1", type: "user", label: "John Smith", risk_score: 0.02, properties: { country: "US", account_age: 1200 } },
  ],
  edges: [
    { id: "e1", source: "usr_8d2f1", target: "mrc_electronics", type: "paid_to", weight: 5 },
    { id: "e2", source: "usr_8d2f1", target: "dev_iphone15_x1", type: "connected_to", weight: 1 },
    { id: "e3", source: "usr_mule_1", target: "dev_iphone15_x1", type: "shares_device", weight: 1 },
    { id: "e4", source: "usr_mule_2", target: "dev_iphone15_x1", type: "shares_device", weight: 1 },
    { id: "e5", source: "usr_mule_3", target: "dev_iphone15_x1", type: "shares_device", weight: 1 },
    { id: "e6", source: "usr_8d2f1", target: "ip_185_234", type: "shares_ip", weight: 1 },
    { id: "e7", source: "usr_mule_1", target: "ip_185_234", type: "shares_ip", weight: 1 },
    { id: "e8", source: "usr_8d2f1", target: "card_visa_ending_4421", type: "owns", weight: 1 },
    { id: "e9", source: "usr_8d2f1", target: "usr_mule_1", type: "transferred_to", weight: 3 },
    { id: "e10", source: "usr_mule_1", target: "usr_mule_2", type: "transferred_to", weight: 2 },
    { id: "e11", source: "usr_mule_2", target: "mrc_fx_broker", type: "paid_to", weight: 4 },
    { id: "e12", source: "usr_3a9c2", target: "dev_pixel8_new", type: "connected_to", weight: 1 },
    { id: "e13", source: "usr_regular_1", target: "mrc_electronics", type: "paid_to", weight: 1 },
  ],
};

export const mockCommunities: Community[] = [
  { community_id: "comm_1", size: 5, risk_score: 0.91, node_ids: ["usr_8d2f1", "usr_mule_1", "usr_mule_2", "usr_mule_3", "mrc_fx_broker"], label: "Fraud Ring Alpha — Device Sharing Cluster" },
  { community_id: "comm_2", size: 2, risk_score: 0.45, node_ids: ["usr_3a9c2", "dev_pixel8_new"], label: "Isolated High-Value Sender" },
];
