import { useCallback, useEffect, useMemo, useState } from "react";
import { alertRecommendationApi } from "./services/alertRecommendationApi";
import { analyticsApi } from "./services/analyticsApi";
import { apiPost } from "./services/apiClient";
import { behaviorApi, type BehaviorEventInput } from "./services/behaviorApi";
import { reportApi } from "./services/reportApi";
import "./styles.css";

type ViewKey = "overview" | "behavior" | "funnel" | "products" | "profiles" | "alerts" | "recommendations" | "reports" | "audit";
type InternalRole = "administrator" | "operations_manager" | "analyst" | "customer_service_viewer" | "read_only_viewer";
type PortalRole = InternalRole | "customer";
type ActionType = "browse" | "click" | "search" | "favorite" | "cart_add" | "order_submit" | "payment_success";

interface PortalProfile {
  loginId: string;
  role: PortalRole;
  name: string;
  title: string;
  description: string;
  dataScope: string;
  scopeLabel: string;
  workspace: "internal" | "customer";
  allowedViews: ViewKey[];
  defaultView: ViewKey;
  canOperate: boolean;
  canExport: boolean;
}

interface Product {
  id: string;
  name: string;
  brand: string;
  category: string;
  price: number;
  rating: number;
  sold: number;
  stock: number;
  tag: string;
  description: string;
  recommendation: string;
  image: string;
}

interface BehaviorRecord {
  event_id?: string;
  eventId?: string;
  event_type?: string;
  eventType?: string;
  user_id?: string;
  userId?: string;
  visitor_id?: string;
  visitorId?: string;
  product_id?: string;
  productId?: string;
  channel_id?: string;
  channelId?: string;
  search_keyword?: string;
  searchKeyword?: string;
  occurred_at?: string;
  occurredAt?: string;
  idempotency_state?: string;
  idempotencyState?: string;
  metadata?: Record<string, unknown>;
}

interface SummaryResponse {
  metrics: Array<{ key: string; name: string; value: number; unit: string; metricVersion: string }>;
  sourceDistribution: Record<string, number>;
  searchKeywords: Record<string, number>;
  freshnessAt: string;
}

interface FunnelResponse {
  stages: Array<{ stage: string; enteredCount: number; convertedCount: number; dropoffCount: number; conversionRate: number; dropoffRate: number }>;
  biggestDropoffStage: string;
  freshnessAt: string;
}

interface AlertItem {
  alertId: string;
  alertType: string;
  severity: string;
  status: string;
  triggerReason: string;
}

interface RecommendationItem {
  product: Product;
  score: number;
  reasons: string[];
}

interface ProductStats {
  productId: string;
  productName: string;
  category: string;
  browse: number;
  click: number;
  favorite: number;
  cartAdd: number;
  order: number;
  payment: number;
  conversionRate: number;
  price: number;
}

interface UserProfileStats {
  userId: string;
  visits: number;
  clicks: number;
  favorites: number;
  carts: number;
  orders: number;
  payments: number;
  paidAmount: number;
  avgPrice: number;
  valueLevel: string;
  intentLevel: string;
  segment: string;
  browseCategory: Record<string, number>;
  favoriteCategory: Record<string, number>;
  purchaseCategory: Record<string, number>;
  priceBand: Record<string, number>;
}

const navItems: Array<{ key: ViewKey; label: string; caption: string }> = [
  { key: "overview", label: "运营总览", caption: "核心指标" },
  { key: "behavior", label: "行为明细", caption: "路径追踪" },
  { key: "funnel", label: "转化漏斗", caption: "流失定位" },
  { key: "products", label: "商品热度", caption: "排行转化" },
  { key: "profiles", label: "用户画像", caption: "分群意向" },
  { key: "alerts", label: "预警中心", caption: "风险处置" },
  { key: "recommendations", label: "智能推荐", caption: "算法解释" },
  { key: "reports", label: "报表统计", caption: "分析输出" },
  { key: "audit", label: "审计日志", caption: "安全留痕" },
];

const portalProfiles: PortalProfile[] = [
  {
    loginId: "admin001",
    role: "administrator",
    name: "系统管理员",
    title: "系统与权限管理工作台",
    description: "管理账号、权限、系统数据重置、审计日志和全量配置。",
    dataScope: "all",
    scopeLabel: "全平台数据",
    workspace: "internal",
    allowedViews: ["overview", "behavior", "funnel", "products", "profiles", "alerts", "recommendations", "reports", "audit"],
    defaultView: "overview",
    canOperate: true,
    canExport: true,
  },
  {
    loginId: "ops001",
    role: "operations_manager",
    name: "运营经理",
    title: "运营分析与转化提升工作台",
    description: "查看实时指标、商品热度、转化漏斗、预警和运营报表。",
    dataScope: "all",
    scopeLabel: "运营全域数据",
    workspace: "internal",
    allowedViews: ["overview", "behavior", "funnel", "products", "profiles", "alerts", "recommendations", "reports"],
    defaultView: "overview",
    canOperate: true,
    canExport: true,
  },
  {
    loginId: "analyst001",
    role: "analyst",
    name: "数据分析师",
    title: "分析建模与指标诊断工作台",
    description: "聚焦行为明细、转化分析、画像分层、推荐解释和报表分析。",
    dataScope: "assigned_segment",
    scopeLabel: "指定分群数据",
    workspace: "internal",
    allowedViews: ["overview", "behavior", "funnel", "products", "profiles", "recommendations", "reports"],
    defaultView: "funnel",
    canOperate: false,
    canExport: true,
  },
  {
    loginId: "service001",
    role: "customer_service_viewer",
    name: "客服主管",
    title: "用户服务与风险跟进工作台",
    description: "查看用户路径、画像和风险提醒，敏感信息默认脱敏。",
    dataScope: "assigned_channel",
    scopeLabel: "分配渠道数据",
    workspace: "internal",
    allowedViews: ["behavior", "profiles", "alerts"],
    defaultView: "behavior",
    canOperate: true,
    canExport: false,
  },
  {
    loginId: "viewer001",
    role: "read_only_viewer",
    name: "只读查看员",
    title: "只读监控工作台",
    description: "只能查看核心指标、漏斗、商品热度和已发布报表。",
    dataScope: "all",
    scopeLabel: "只读数据",
    workspace: "internal",
    allowedViews: ["overview", "funnel", "products", "reports"],
    defaultView: "overview",
    canOperate: false,
    canExport: false,
  },
  {
    loginId: "user001",
    role: "customer",
    name: "林一诺",
    title: "高价值运动用户",
    description: "偏好运动鞋服和数码装备，价格承受能力较高。",
    dataScope: "self",
    scopeLabel: "本人行为数据",
    workspace: "customer",
    allowedViews: [],
    defaultView: "overview",
    canOperate: true,
    canExport: false,
  },
  {
    loginId: "user002",
    role: "customer",
    name: "周雨晴",
    title: "价格敏感家庭用户",
    description: "偏好食品、母婴、家居，关注低价与高销量。",
    dataScope: "self",
    scopeLabel: "本人行为数据",
    workspace: "customer",
    allowedViews: [],
    defaultView: "overview",
    canOperate: true,
    canExport: false,
  },
  {
    loginId: "user003",
    role: "customer",
    name: "陈亦航",
    title: "潜力数码用户",
    description: "频繁浏览数码和箱包，容易收藏加购但支付较少。",
    dataScope: "self",
    scopeLabel: "本人行为数据",
    workspace: "customer",
    allowedViews: [],
    defaultView: "overview",
    canOperate: true,
    canExport: false,
  },
];

const customerSeeds: Record<string, { categories: string[]; maxPrice: number; keywords: string[] }> = {
  user001: { categories: ["鞋服", "服饰", "数码", "运动"], maxPrice: 1200, keywords: ["跑鞋", "手表", "夹克"] },
  user002: { categories: ["食品", "母婴", "家居", "美妆"], maxPrice: 350, keywords: ["低糖", "儿童", "水壶"] },
  user003: { categories: ["数码", "箱包", "家居"], maxPrice: 900, keywords: ["耳机", "背包", "办公"] },
};

const categoryCatalog = [
  {
    category: "鞋服",
    image: "/assets/products/shoes.jpg",
    brands: ["StrideLab", "Runova", "UrbanStep", "FitRoad"],
    names: ["云感缓震跑鞋", "轻量训练鞋", "城市复古板鞋", "竞速慢跑鞋", "透气徒步鞋"],
    desc: "轻量缓震鞋底，适合通勤、慢跑和日常训练。",
    min: 199,
    max: 699,
  },
  {
    category: "服饰",
    image: "/assets/products/apparel.jpg",
    brands: ["Northline", "WarmGo", "ModeKit", "AirWeave"],
    names: ["城市机能夹克", "轻薄羽绒服", "速干运动 T 恤", "高弹休闲裤", "防晒连帽外套"],
    desc: "舒适面料与通勤版型结合，覆盖日常、运动和轻户外场景。",
    min: 129,
    max: 899,
  },
  {
    category: "箱包",
    image: "/assets/products/bag.jpg",
    brands: ["CarryOne", "Voyago", "PackLab", "MetroBag"],
    names: ["通勤分仓背包", "轻旅登机箱", "防泼水斜挎包", "大容量旅行包", "电脑双肩包"],
    desc: "多分区收纳设计，满足上班、差旅和短途出行。",
    min: 99,
    max: 999,
  },
  {
    category: "数码",
    image: "/assets/products/digital.jpg",
    brands: ["PulseFit", "SoundMax", "NovaTech", "LinkPro"],
    names: ["健康监测手表", "降噪蓝牙耳机", "磁吸充电宝", "便携蓝牙音箱", "高清运动相机"],
    desc: "围绕移动办公、运动健康和娱乐体验的智能硬件。",
    min: 159,
    max: 1299,
  },
  {
    category: "美妆",
    image: "/assets/products/beauty.jpg",
    brands: ["ClearSkin", "GlowMe", "PureLab", "AromaCare"],
    names: ["控油精华套装", "修护面霜", "防晒隔离乳", "温和洁面泡沫", "补水面膜礼盒"],
    desc: "温和配方，覆盖清洁、保湿、防晒和修护需求。",
    min: 59,
    max: 399,
  },
  {
    category: "家居",
    image: "/assets/products/home.jpg",
    brands: ["SeatWell", "HomeEase", "LiteHome", "ComfortX"],
    names: ["人体工学办公椅", "智能恒温水壶", "护眼台灯", "多功能收纳架", "无线吸尘器"],
    desc: "面向居家办公和生活效率的实用家居商品。",
    min: 89,
    max: 1599,
  },
  {
    category: "食品",
    image: "/assets/products/food.jpg",
    brands: ["GrainJoy", "NutriBox", "DailyBite", "FreshWay"],
    names: ["低糖燕麦礼盒", "坚果能量包", "黑咖啡组合", "高蛋白代餐", "果干零食桶"],
    desc: "低糖、高纤、独立包装，适合早餐、健身和办公室场景。",
    min: 29,
    max: 249,
  },
  {
    category: "母婴",
    image: "/assets/products/baby.jpg",
    brands: ["KidSafe", "BabyJoy", "TinyCare", "MomoKid"],
    names: ["儿童防摔保温杯", "婴儿柔纸巾", "儿童学习餐具", "宝宝湿巾组合", "亲子出行背带"],
    desc: "重视安全材质和亲子场景，适合家庭日常补货。",
    min: 29,
    max: 399,
  },
  {
    category: "运动",
    image: "/assets/products/sports.jpg",
    brands: ["FitCore", "YogaWay", "PowerRun", "ActivePro"],
    names: ["瑜伽训练垫", "可调节哑铃", "运动护膝", "筋膜放松器", "智能跳绳"],
    desc: "覆盖居家训练、拉伸恢复和基础运动保护。",
    min: 49,
    max: 699,
  },
  {
    category: "旅行",
    image: "/assets/products/travel.jpg",
    brands: ["TripGo", "LightTrip", "RoadKit", "SkyPack"],
    names: ["旅行收纳套装", "便携洗漱包", "颈枕眼罩套装", "折叠出行包", "证件收纳夹"],
    desc: "小体积、多收纳，适合短途旅行和商务差旅。",
    min: 39,
    max: 329,
  },
];

const eventLabels: Record<ActionType | string, string> = {
  browse: "浏览",
  click: "点击",
  search: "搜索",
  favorite: "收藏",
  cart_add: "加购",
  order_submit: "下单",
  payment_success: "支付成功",
};

const stageLabels: Record<string, string> = { browse: "浏览", click: "点击", cart: "加购", order: "下单", payment: "支付" };
const channelLabels: Record<string, string> = { search: "搜索", recommendation: "推荐", campaign: "活动页", store: "门店", direct: "直接访问" };
const roleLabels: Record<PortalRole, string> = {
  administrator: "系统管理员",
  operations_manager: "运营经理",
  analyst: "数据分析师",
  customer_service_viewer: "客服主管",
  read_only_viewer: "只读查看员",
  customer: "零售用户",
};
const pieColors = ["#206a5d", "#5887d8", "#b36b18", "#8d62c4", "#c7534a", "#48916d", "#79879a", "#2f6f9f"];

const products = generateProducts();
const productById = new Map(products.map((product) => [product.id, product]));
const fallbackReports = ["用户行为明细", "商品分析报表", "转化漏斗报表", "用户画像报表", "用户分群报表", "销售转化报表", "运营效果报表"];

function App() {
  const [loginId, setLoginId] = useState("ops001");
  const [portal, setPortal] = useState<PortalProfile | null>(null);
  const [loginError, setLoginError] = useState("");
  const [activeView, setActiveView] = useState<ViewKey>("overview");
  const [dateRange, setDateRange] = useState("今日");
  const [channel, setChannel] = useState("全部渠道");
  const [keyword, setKeyword] = useState("");
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [funnel, setFunnel] = useState<FunnelResponse | null>(null);
  const [events, setEvents] = useState<BehaviorRecord[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [reports, setReports] = useState<Array<Record<string, unknown>>>([]);
  const [auditLogs, setAuditLogs] = useState<Array<Record<string, unknown>>>([]);
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState("");
  const [systemMessage, setSystemMessage] = useState("");
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [shopSearch, setShopSearch] = useState("");
  const [shopCategory, setShopCategory] = useState("全部");
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [cart, setCart] = useState<string[]>([]);
  const [lastUserAction, setLastUserAction] = useState("还没有产生用户行为");
  const [sessionId, setSessionId] = useState(() => `session-${Date.now().toString(36)}`);

  const currentCustomerId = portal?.role === "customer" ? portal.loginId : "user001";
  const availableNavItems = useMemo(() => navItems.filter((item) => portal?.allowedViews.includes(item.key)), [portal]);
  const activeMeta = navItems.find((item) => item.key === activeView) ?? navItems[0];
  const categories = useMemo(() => ["全部", ...categoryCatalog.map((item) => item.category)], []);
  const productSales = useMemo(() => buildProductSales(events), [events]);
  const productsWithSales = useMemo(() => applyProductSales(products, productSales), [productSales]);
  const selectedProductWithSales = useMemo(
    () => (selectedProduct ? (productsWithSales.find((product) => product.id === selectedProduct.id) ?? selectedProduct) : null),
    [productsWithSales, selectedProduct],
  );
  const productStats = useMemo(() => buildProductStats(events, productsWithSales), [events, productsWithSales]);
  const metricCards = useMemo(() => buildMetricCards(summary, events), [summary, events]);
  const userProfiles = useMemo(() => buildUserProfiles(events), [events]);
  const recommendations = useMemo(() => recommendProductsForUser(currentCustomerId, events, 10, productsWithSales), [currentCustomerId, events, productsWithSales]);
  const recentEvents = useMemo(() => filterEvents(events, channel, keyword).slice(-14).reverse(), [events, channel, keyword]);
  const visibleProducts = useMemo(() => {
    const search = shopSearch.trim().toLowerCase();
    const seed = customerSeeds[currentCustomerId];
    return productsWithSales
      .filter((product) => {
        const categoryMatched = shopCategory === "全部" || product.category === shopCategory;
        const searchText = `${product.name} ${product.brand} ${product.category} ${product.tag} ${product.description}`.toLowerCase();
        const searchMatched = !search || searchText.includes(search);
        return categoryMatched && searchMatched;
      })
      .sort((a, b) => {
        const aBoost = seed?.categories.includes(a.category) ? 1 : 0;
        const bBoost = seed?.categories.includes(b.category) ? 1 : 0;
        return bBoost - aBoost || b.sold - a.sold;
      });
  }, [currentCustomerId, productsWithSales, shopCategory, shopSearch]);

  const handleLogin = useCallback(
    (id = loginId) => {
      const matched = portalProfiles.find((profile) => profile.loginId === id.trim().toLowerCase());
      if (!matched) {
        setLoginError("登录 ID 不存在，请使用下方演示账号。");
        return;
      }
      setPortal(matched);
      setActiveView(matched.defaultView);
      setLoginError("");
      setShopSearch("");
      setShopCategory("全部");
      setSelectedProduct(null);
      setCart([]);
      setSessionId(`session-${Date.now().toString(36)}`);
      window.localStorage.setItem(
        "retail-auth",
        JSON.stringify({
          actorId: matched.loginId,
          role: matched.role === "customer" ? "read_only_viewer" : matched.role,
          dataScope: matched.dataScope === "self" ? "none" : matched.dataScope,
        }),
      );
    },
    [loginId],
  );

  const refreshData = useCallback(async () => {
    if (!portal) return;
    setLoading(true);
    const tasks: Array<[string, Promise<unknown>]> = [
      ["核心指标", analyticsApi.summary()],
      ["转化漏斗", analyticsApi.funnel()],
      ["行为明细", behaviorApi.list()],
    ];
    if (portal.allowedViews.includes("alerts")) tasks.push(["预警", alertRecommendationApi.alerts()]);
    if (portal.allowedViews.includes("reports")) tasks.push(["报表", reportApi.reports()]);
    if (portal.allowedViews.includes("audit")) tasks.push(["审计日志", reportApi.auditLogs()]);

    const settled = await Promise.allSettled(tasks.map(([, promise]) => promise));
    const errors: string[] = [];
    settled.forEach((result, index) => {
      const label = tasks[index][0];
      if (result.status === "rejected") {
        errors.push(label);
        return;
      }
      if (label === "核心指标") setSummary(result.value as SummaryResponse);
      if (label === "转化漏斗") setFunnel(result.value as FunnelResponse);
      if (label === "行为明细") setEvents(result.value as BehaviorRecord[]);
      if (label === "预警") setAlerts(((result.value as { items?: AlertItem[] }).items ?? []) as AlertItem[]);
      if (label === "报表") setReports(((result.value as { items?: Array<Record<string, unknown>> }).items ?? []) as Array<Record<string, unknown>>);
      if (label === "审计日志") setAuditLogs(((result.value as { items?: Array<Record<string, unknown>> }).items ?? []) as Array<Record<string, unknown>>);
    });
    setApiError(errors.length ? `${errors.join("、")}接口暂时不可用，请确认后端已启动并已重启到最新代码。` : "");
    setLoading(false);
  }, [portal]);

  useEffect(() => {
    if (!portal) return;
    if (portal.workspace === "internal" && !portal.allowedViews.includes(activeView)) setActiveView(portal.defaultView);
  }, [activeView, portal]);

  useEffect(() => {
    void refreshData();
  }, [refreshData]);

  useEffect(() => {
    if (!autoRefresh || !portal) return undefined;
    const timer = window.setInterval(() => void refreshData(), 5000);
    return () => window.clearInterval(timer);
  }, [autoRefresh, portal, refreshData]);

  const createEvent = useCallback(
    (eventType: ActionType, product: Product, index = 0, extra: Partial<BehaviorEventInput> = {}): BehaviorEventInput => {
      const now = Date.now() + index * 1000;
      return {
        eventId: `${sessionId}-${eventType}-${product.id}-${now}-${Math.random().toString(36).slice(2, 8)}`,
        sourceSystem: "customer-web",
        eventType,
        userId: currentCustomerId,
        sessionId,
        productId: product.id,
        channelId: extra.channelId ?? "direct",
        occurredAt: new Date(now).toISOString(),
        searchKeyword: eventType === "search" ? shopSearch : extra.searchKeyword,
        metadata: {
          productName: product.name,
          brand: product.brand,
          price: product.price,
          category: product.category,
          tag: product.tag,
          image: product.image,
          scene: "用户购物端",
        },
        ...extra,
      };
    },
    [currentCustomerId, sessionId, shopSearch],
  );

  const submitEvents = useCallback(
    async (newEvents: BehaviorEventInput[], label: string) => {
      setLoading(true);
      setApiError("");
      try {
        const result = (await behaviorApi.ingest(newEvents)) as { acceptedCount?: number };
        setLastUserAction(`${label}：写入 ${result.acceptedCount ?? newEvents.length} 条行为事件`);
        await refreshData();
      } catch (error) {
        setApiError(error instanceof Error ? error.message : "行为事件写入失败");
      } finally {
        setLoading(false);
      }
    },
    [refreshData],
  );

  const openProduct = (product: Product) => {
    setSelectedProduct(product);
    void submitEvents([createEvent("browse", product, 0, { channelId: "recommendation" }), createEvent("click", product, 1)], `查看 ${product.name}`);
  };

  const emitSearch = () => {
    const target = visibleProducts[0] ?? productsWithSales[0];
    void submitEvents([createEvent("search", target, 0, { channelId: "search", searchKeyword: shopSearch || target.category })], `搜索“${shopSearch || target.category}”`);
  };

  const emitSingleAction = (eventType: ActionType, product: Product) => {
    if (eventType === "cart_add") setCart((items) => Array.from(new Set([...items, product.id])));
    void submitEvents([createEvent(eventType, product)], `${product.name} ${eventLabels[eventType]}`);
  };

  const emitPurchase = (product: Product) => {
    const orderId = `order-${Date.now().toString(36)}`;
    const journey: ActionType[] = ["browse", "click", "cart_add", "order_submit", "payment_success"];
    setCart((items) => Array.from(new Set([...items, product.id])));
    void submitEvents(
      journey.map((eventType, index) =>
        createEvent(eventType, product, index, {
          channelId: index === 0 ? "recommendation" : "direct",
          orderId: eventType === "order_submit" || eventType === "payment_success" ? orderId : undefined,
          paymentId: eventType === "payment_success" ? `pay-${Date.now().toString(36)}` : undefined,
        }),
      ),
      `${product.name} 完整购买路径`,
    );
  };

  const resetSystemData = async () => {
    setLoading(true);
    setSystemMessage("");
    try {
      await apiPost("/system/reset", {});
      setEvents([]);
      setAuditLogs([]);
      setAlerts([]);
      setReports([]);
      setSummary(null);
      setFunnel(null);
      setSystemMessage("系统行为、指标和审计演示数据已重置。");
      await refreshData();
    } catch (error) {
      setSystemMessage(error instanceof Error ? error.message : "系统重置失败");
    } finally {
      setLoading(false);
    }
  };

  if (!portal) {
    return <LoginScreen loginId={loginId} loginError={loginError} setLoginId={setLoginId} onLogin={handleLogin} />;
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-mark">R</div>
          <div>
            <strong>智能零售分析</strong>
            <span>统一行为数据平台</span>
          </div>
        </div>

        <div className="account-card">
          <span>当前登录</span>
          <strong>{portal.loginId}</strong>
          <small>{roleLabels[portal.role]} · {portal.scopeLabel}</small>
          <button type="button" onClick={() => setPortal(null)}>切换账号</button>
        </div>

        {portal.workspace === "internal" ? (
          <nav className="nav-list" aria-label="主导航">
            {availableNavItems.map((item) => (
              <button className={item.key === activeView ? "nav-item active" : "nav-item"} key={item.key} onClick={() => setActiveView(item.key)} type="button">
                <span>{item.label}</span>
                <small>{item.caption}</small>
              </button>
            ))}
          </nav>
        ) : (
          <div className="session-card">
            <span>用户身份</span>
            <strong>{portal.name}</strong>
            <small>{sessionId}</small>
          </div>
        )}
      </aside>

      <main className="workspace">
        {portal.workspace === "internal" ? (
          <>
            <header className="topbar">
              <div>
                <p className="eyebrow">{portal.title}</p>
                <h1>{activeMeta.label}</h1>
              </div>
              <div className="topbar-actions">
                <span className="freshness">{loading ? "处理中" : `数据刷新：${formatFreshness(summary?.freshnessAt)}`}</span>
                <label className="toggle-line">
                  <input type="checkbox" checked={autoRefresh} onChange={(event) => setAutoRefresh(event.target.checked)} />
                  5 秒自动刷新
                </label>
                <button type="button" className="primary-action" onClick={() => void refreshData()}>刷新数据</button>
              </div>
            </header>

            <section className="role-banner">
              <strong>{portal.name}</strong>
              <span>{portal.description}</span>
              {!portal.canOperate && <b>当前角色为只读或分析权限，操作按钮会受限。</b>}
              {portal.role === "administrator" && (
                <label className="danger-switch">
                  <input
                    type="checkbox"
                    onChange={(event) => {
                      if (event.target.checked) void resetSystemData();
                      event.target.checked = false;
                    }}
                  />
                  重置系统演示数据
                </label>
              )}
            </section>

            {systemMessage && <div className="notice">{systemMessage}</div>}
            {apiError && <div className="notice error">{apiError}</div>}

            <section className="filter-bar" aria-label="分析筛选">
              <label>
                时间
                <select value={dateRange} onChange={(event) => setDateRange(event.target.value)}>
                  <option>今日</option>
                  <option>近7天</option>
                  <option>近30天</option>
                </select>
              </label>
              <label>
                渠道
                <select value={channel} onChange={(event) => setChannel(event.target.value)}>
                  <option>全部渠道</option>
                  <option>搜索</option>
                  <option>推荐</option>
                  <option>活动页</option>
                  <option>门店</option>
                  <option>直接访问</option>
                </select>
              </label>
              <label className="search-field">
                商品 / 用户
                <input value={keyword} onChange={(event) => setKeyword(event.target.value)} placeholder="输入商品、用户或关键词" />
              </label>
              <button type="button" className="ghost-action" onClick={() => setKeyword("")}>重置</button>
            </section>

            {activeView === "overview" && <Overview metricCards={metricCards} funnel={funnel} productStats={productStats} alerts={alerts} sourceDistribution={summary?.sourceDistribution ?? {}} />}
            {activeView === "behavior" && <BehaviorView rows={recentEvents} />}
            {activeView === "funnel" && <FunnelView funnel={funnel} />}
            {activeView === "products" && <ProductView rows={productStats} />}
            {activeView === "profiles" && <ProfileView profiles={userProfiles} />}
            {activeView === "alerts" && <AlertView alerts={alerts} canOperate={portal.canOperate} />}
            {activeView === "recommendations" && <RecommendationView recommendations={recommendProductsForUser("all", events, 10, productsWithSales)} />}
            {activeView === "reports" && <ReportView reports={reports} canExport={portal.canExport} />}
            {activeView === "audit" && <AuditView rows={auditLogs} />}

            <footer className="status-strip">
              <span>登录 ID：{portal.loginId}</span>
              <span>角色：{roleLabels[portal.role]}</span>
              <span>数据范围：{portal.scopeLabel}</span>
              <span>商品数：{products.length}</span>
              <span>事件数：{events.length}</span>
            </footer>
          </>
        ) : (
          <CustomerWorkspace
            portal={portal}
            cart={cart}
            loading={loading}
            search={shopSearch}
            setSearch={setShopSearch}
            category={shopCategory}
            setCategory={setShopCategory}
            categories={categories}
            products={visibleProducts}
            recommendations={recommendations}
            selectedProduct={selectedProductWithSales}
            lastUserAction={lastUserAction}
            onSearch={emitSearch}
            onOpenProduct={openProduct}
            onCloseProduct={() => setSelectedProduct(null)}
            onSingleAction={emitSingleAction}
            onPurchase={emitPurchase}
          />
        )}
      </main>
    </div>
  );
}

function LoginScreen({ loginId, loginError, setLoginId, onLogin }: { loginId: string; loginError: string; setLoginId: (value: string) => void; onLogin: (id?: string) => void }) {
  return (
    <main className="login-screen">
      <section className="login-copy">
        <div className="brand-mark">R</div>
        <p className="eyebrow">Retail Behavior Analytics</p>
        <h1>按登录 ID 进入不同工作台</h1>
        <p>5 个内部角色和 3 个用户端共用同一套后端行为数据、指标、推荐、画像和审计链路。</p>
      </section>
      <section className="login-card">
        <form
          onSubmit={(event) => {
            event.preventDefault();
            onLogin();
          }}
        >
          <label>
            登录 ID
            <input value={loginId} onChange={(event) => setLoginId(event.target.value)} />
          </label>
          {loginError && <div className="notice error">{loginError}</div>}
          <button type="submit" className="primary-action">进入系统</button>
        </form>
        <div className="role-grid">
          {portalProfiles.map((profile) => (
            <button
              type="button"
              className="role-tile"
              key={profile.loginId}
              onClick={() => {
                setLoginId(profile.loginId);
                onLogin(profile.loginId);
              }}
            >
              <strong>{profile.loginId}</strong>
              <span>{profile.name}</span>
              <small>{profile.title}</small>
            </button>
          ))}
        </div>
      </section>
    </main>
  );
}

function Overview({
  metricCards,
  funnel,
  productStats,
  alerts,
  sourceDistribution,
}: {
  metricCards: ReturnType<typeof buildMetricCards>;
  funnel: FunnelResponse | null;
  productStats: ProductStats[];
  alerts: AlertItem[];
  sourceDistribution: Record<string, number>;
}) {
  return (
    <div className="content-grid">
      <section className="metric-grid full-span">
        {metricCards.map((metric) => (
          <article className="metric-card" key={metric.key}>
            <span>{metric.label}</span>
            <strong>{metric.value}</strong>
            <em className={metric.tone}>{metric.delta}</em>
          </article>
        ))}
      </section>
      <section className="panel wide">
        <PanelTitle title="转化漏斗" meta="用户访问到支付的完整路径" />
        <FunnelBars funnel={funnel} />
      </section>
      <section className="panel">
        <PanelTitle title="渠道来源" meta="实时统计用户来源" />
        <div className="source-list">
          {Object.entries(sourceDistribution).length ? (
            Object.entries(sourceDistribution).map(([source, value]) => (
              <div className="source-row" key={source}>
                <span>{channelLabels[source] ?? source}</span>
                <strong>{value}</strong>
              </div>
            ))
          ) : (
            <EmptyState text="暂无来源数据，使用用户端产生行为后会变化。" />
          )}
        </div>
      </section>
      <section className="panel wide">
        <PanelTitle title="商品热度排行" meta="按行为热度和支付转化排序" />
        <ProductTable rows={productStats.slice(0, 8)} />
      </section>
      <section className="panel">
        <PanelTitle title="预警概览" meta={`${alerts.length} 条待关注`} />
        <div className="alert-list">
          {alerts.length ? alerts.slice(0, 4).map((alert) => <AlertRow alert={alert} key={alert.alertId} />) : <EmptyState text="当前没有预警。" />}
        </div>
      </section>
    </div>
  );
}

function BehaviorView({ rows }: { rows: BehaviorRecord[] }) {
  return (
    <section className="panel full-span">
      <PanelTitle title="用户行为明细" meta="浏览、点击、搜索、收藏、加购、下单、支付行为可追溯" />
      {rows.length ? (
        <table>
          <thead>
            <tr>
              <th>时间</th>
              <th>用户</th>
              <th>行为</th>
              <th>商品</th>
              <th>渠道</th>
              <th>幂等状态</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => {
              const eventType = readField(row, "eventType", "event_type");
              const productId = readField(row, "productId", "product_id");
              const channelId = readField(row, "channelId", "channel_id");
              return (
                <tr key={readField(row, "eventId", "event_id")}>
                  <td>{formatTime(readField(row, "occurredAt", "occurred_at"))}</td>
                  <td>{maskUser(getEventUser(row))}</td>
                  <td>{eventLabels[eventType] ?? eventType}</td>
                  <td>{productName(row, productId)}</td>
                  <td>{channelLabels[channelId] ?? channelId}</td>
                  <td className={`state ${readField(row, "idempotencyState", "idempotency_state") || "accepted"}`}>
                    {readField(row, "idempotencyState", "idempotency_state") || "accepted"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      ) : (
        <EmptyState text="还没有行为事件。用 user001、user002、user003 登录并操作商品后，这里会刷新。" />
      )}
    </section>
  );
}

function FunnelView({ funnel }: { funnel: FunnelResponse | null }) {
  return (
    <section className="panel full-span">
      <PanelTitle title="转化漏斗分析" meta="定位浏览、点击、加购、下单、支付的流失环节" />
      <FunnelBars funnel={funnel} />
    </section>
  );
}

function ProductView({ rows }: { rows: ProductStats[] }) {
  return (
    <section className="panel full-span">
      <PanelTitle title="商品热度分析" meta="浏览、点击、加购、收藏、购买和转化率排行" />
      <ProductTable rows={rows.slice(0, 30)} />
    </section>
  );
}

function ProfileView({ profiles }: { profiles: UserProfileStats[] }) {
  const highValue = profiles.filter((profile) => profile.valueLevel === "高价值").length;
  const potential = profiles.filter((profile) => profile.segment === "潜力用户").length;
  const highIntent = profiles.filter((profile) => profile.intentLevel === "高").length;
  const categoryTotal = mergeCounts(profiles.map((profile) => profile.browseCategory));
  const favoriteTotal = mergeCounts(profiles.map((profile) => profile.favoriteCategory));
  const purchaseTotal = mergeCounts(profiles.map((profile) => profile.purchaseCategory));
  const priceTotal = mergeCounts(profiles.map((profile) => profile.priceBand));

  return (
    <div className="profile-layout">
      <section className="metric-grid full-span">
        <article className="metric-card"><span>高价值用户</span><strong>{highValue}</strong><em className="good">支付金额 ≥ 1000 或支付 ≥ 3 次</em></article>
        <article className="metric-card"><span>潜力用户</span><strong>{potential}</strong><em className="warn">加购/收藏活跃但支付不足</em></article>
        <article className="metric-card"><span>高购买意向</span><strong>{highIntent}</strong><em className="good">意向分 ≥ 70</em></article>
        <article className="metric-card"><span>画像样本</span><strong>{profiles.length}</strong><em>3 个用户账号</em></article>
      </section>

      <section className="profile-pies full-span">
        <PieChart title="浏览类目偏好" data={categoryTotal} />
        <PieChart title="收藏类目偏好" data={favoriteTotal} />
        <PieChart title="购买类目偏好" data={purchaseTotal} />
        <PieChart title="浏览价位偏好" data={priceTotal} />
      </section>

      <section className="panel full-span">
        <PanelTitle title="用户画像算法标准" meta="高价值、潜力、购买意向均由行为事件实时计算" />
        <table>
          <thead>
            <tr>
              <th>用户</th>
              <th>分群</th>
              <th>价值等级</th>
              <th>购买意向</th>
              <th>浏览</th>
              <th>收藏</th>
              <th>加购</th>
              <th>支付</th>
              <th>支付金额</th>
              <th>客单价</th>
            </tr>
          </thead>
          <tbody>
            {profiles.map((profile) => (
              <tr key={profile.userId}>
                <td>{profile.userId}</td>
                <td>{profile.segment}</td>
                <td>{profile.valueLevel}</td>
                <td>{profile.intentLevel}</td>
                <td>{profile.visits}</td>
                <td>{profile.favorites}</td>
                <td>{profile.carts}</td>
                <td>{profile.payments}</td>
                <td>￥{profile.paidAmount.toLocaleString()}</td>
                <td>￥{profile.avgPrice.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

function AlertView({ alerts, canOperate }: { alerts: AlertItem[]; canOperate: boolean }) {
  return (
    <section className="panel full-span">
      <PanelTitle title="用户预警管理" meta="低活跃、流失风险、转化异常、行为数据异常" />
      <div className="alert-list large">
        {alerts.length ? alerts.map((alert) => <AlertRow alert={alert} key={alert.alertId} withAction canOperate={canOperate} />) : <EmptyState text="当前没有预警。" />}
      </div>
    </section>
  );
}

function RecommendationView({ recommendations }: { recommendations: RecommendationItem[] }) {
  return (
    <section className="panel full-span">
      <PanelTitle title="智能推荐分析" meta="推荐分 = 用户偏好类目 + 价位匹配 + 商品热度 + 未购买新鲜度" />
      <div className="recommendation-grid">
        {recommendations.map((item) => (
          <article className="recommendation-card rich" key={item.product.id}>
            <img src={item.product.image} alt={item.product.name} />
            <strong>{item.product.name}</strong>
            <span>{item.product.brand} · {item.product.category} · ￥{item.product.price}</span>
            <b>推荐分 {item.score}</b>
            <p>{item.reasons.join("；")}</p>
            <div className="confidence"><i style={{ width: `${Math.min(item.score, 100)}%` }} /></div>
          </article>
        ))}
      </div>
    </section>
  );
}

function ReportView({ reports, canExport }: { reports: Array<Record<string, unknown>>; canExport: boolean }) {
  const names = reports.length ? reports.map((report) => String(report.reportType ?? "operation_effect")) : fallbackReports;
  return (
    <section className="panel full-span">
      <PanelTitle title="报表统计" meta="按权限导出，敏感字段默认脱敏" />
      <div className="report-grid">
        {names.map((report) => (
          <button type="button" className="report-tile" key={report} disabled={!canExport}>
            <strong>{reportLabel(report)}</strong>
            <span>{canExport ? "导出报表" : "只读查看"}</span>
          </button>
        ))}
      </div>
    </section>
  );
}

function AuditView({ rows }: { rows: Array<Record<string, unknown>> }) {
  return (
    <section className="panel full-span">
      <PanelTitle title="审计日志" meta="登录、查询、导出、权限变更、敏感数据访问" />
      {rows.length ? (
        <table>
          <thead>
            <tr>
              <th>时间</th>
              <th>操作者</th>
              <th>动作</th>
              <th>对象</th>
              <th>结果</th>
            </tr>
          </thead>
          <tbody>
            {rows.slice(-12).reverse().map((row, index) => (
              <tr key={`${String(row.audit_id ?? row.auditId ?? "audit")}-${index}`}>
                <td>{formatTime(String(row.created_at ?? row.createdAt ?? ""))}</td>
                <td>{String(row.actor_id ?? row.actorId ?? "demo")}</td>
                <td>{String(row.action ?? "-")}</td>
                <td>{String(row.resource_type ?? row.resourceType ?? "-")}</td>
                <td>{String(row.result ?? "success")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <EmptyState text="暂无审计记录。查询、写入和重置系统后会产生日志。" />
      )}
    </section>
  );
}

function CustomerWorkspace({
  portal,
  cart,
  loading,
  search,
  setSearch,
  category,
  setCategory,
  categories,
  products,
  recommendations,
  selectedProduct,
  lastUserAction,
  onSearch,
  onOpenProduct,
  onCloseProduct,
  onSingleAction,
  onPurchase,
}: {
  portal: PortalProfile;
  cart: string[];
  loading: boolean;
  search: string;
  setSearch: (value: string) => void;
  category: string;
  setCategory: (value: string) => void;
  categories: string[];
  products: Product[];
  recommendations: RecommendationItem[];
  selectedProduct: Product | null;
  lastUserAction: string;
  onSearch: () => void;
  onOpenProduct: (product: Product) => void;
  onCloseProduct: () => void;
  onSingleAction: (eventType: ActionType, product: Product) => void;
  onPurchase: (product: Product) => void;
}) {
  return (
    <>
      <header className="topbar shop-hero">
        <div>
          <p className="eyebrow">{portal.title}</p>
          <h1>{portal.name}的智能购物页</h1>
          <p>{portal.description}</p>
        </div>
        <div className="topbar-actions">
          <span className="freshness">购物车：{cart.length} 件</span>
          <span className="freshness">{loading ? "提交中" : lastUserAction}</span>
        </div>
      </header>

      <section className="shop-toolbar">
        <label>
          搜索商品
          <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="输入跑鞋、耳机、低糖、儿童等关键词" />
        </label>
        <button type="button" className="primary-action" onClick={onSearch}>搜索</button>
      </section>

      <section className="category-strip" aria-label="商品分类">
        {categories.map((item) => (
          <button type="button" className={item === category ? "active" : ""} key={item} onClick={() => setCategory(item)}>
            {item}
          </button>
        ))}
      </section>

      <section className="shop-insight">
        <strong>智能导购</strong>
        <span>当前展示 {products.length} / {products.length ? 100 : 0} 个商品。查看、收藏、加购、购买都会自动采集到后台行为链路。</span>
      </section>

      <section className="panel full-span">
        <PanelTitle title="为你推荐 10 个商品" meta="根据当前用户画像、价位偏好和商品热度计算" />
        <div className="recommendation-grid">
          {recommendations.map((item) => (
            <article className="recommendation-card rich" key={item.product.id}>
              <img src={item.product.image} alt={item.product.name} />
              <strong>{item.product.name}</strong>
              <span>{item.product.category} · ￥{item.product.price}</span>
              <b>推荐分 {item.score}</b>
              <p>{item.reasons.slice(0, 2).join("；")}</p>
              <button type="button" onClick={() => onOpenProduct(item.product)}>查看推荐</button>
            </article>
          ))}
        </div>
      </section>

      <section className="shop-grid">
        {products.slice(0, 100).map((product) => (
          <article className="product-card" key={product.id}>
            <button type="button" className="product-image-button" onClick={() => onOpenProduct(product)}>
              <img src={product.image} alt={product.name} />
              <span>{product.category}</span>
            </button>
            <div className="product-copy">
              <span>{product.brand} · {product.tag}</span>
              <h2>{product.name}</h2>
              <p>{product.description}</p>
              <div className="product-meta">
                <b>{product.rating.toFixed(1)} 分</b>
                <b>销量 {product.sold.toLocaleString()}</b>
                <b>库存 {product.stock}</b>
              </div>
              <strong>￥{product.price}</strong>
            </div>
            <div className="product-actions">
              <button type="button" onClick={() => onOpenProduct(product)}>查看</button>
              <button type="button" onClick={() => onSingleAction("favorite", product)}>收藏</button>
              <button type="button" onClick={() => onSingleAction("cart_add", product)}>加购</button>
              <button type="button" className="primary-action" onClick={() => onPurchase(product)}>立即购买</button>
            </div>
          </article>
        ))}
      </section>

      {!products.length && <EmptyState text="没有匹配商品，换个关键词或分类试试。" />}

      {selectedProduct && (
        <section className="detail-panel">
          <button type="button" className="detail-close" onClick={onCloseProduct}>关闭</button>
          <img className="detail-image" src={selectedProduct.image} alt={selectedProduct.name} />
          <div className="detail-copy">
            <span>{selectedProduct.brand} · {selectedProduct.category} · {selectedProduct.tag}</span>
            <h2>{selectedProduct.name}</h2>
            <p>{selectedProduct.description}</p>
            <p className="recommend-reason">推荐理由：{selectedProduct.recommendation}</p>
            <div className="product-meta">
              <b>{selectedProduct.rating.toFixed(1)} 分</b>
              <b>销量 {selectedProduct.sold.toLocaleString()}</b>
              <b>库存 {selectedProduct.stock}</b>
            </div>
            <strong>￥{selectedProduct.price}</strong>
            <div className="detail-actions">
              <button type="button" onClick={() => onSingleAction("favorite", selectedProduct)}>收藏</button>
              <button type="button" onClick={() => onSingleAction("cart_add", selectedProduct)}>加入购物车</button>
              <button type="button" className="primary-action" onClick={() => onPurchase(selectedProduct)}>下单并支付</button>
            </div>
          </div>
        </section>
      )}
    </>
  );
}

function FunnelBars({ funnel }: { funnel: FunnelResponse | null }) {
  const stages = funnel?.stages ?? [];
  if (!stages.length) return <EmptyState text="暂无漏斗数据。" />;
  return (
    <div className="funnel-bars">
      {stages.map((stage) => (
        <div className="funnel-row" key={stage.stage}>
          <div className="funnel-label">
            <strong>{stageLabels[stage.stage] ?? stage.stage}</strong>
            <span>{stage.enteredCount.toLocaleString()} 人进入</span>
          </div>
          <div className="bar-track"><i style={{ width: `${Math.max(0, Math.min(stage.conversionRate, 100))}%` }} /></div>
          <span className="rate">{stage.conversionRate}%</span>
        </div>
      ))}
    </div>
  );
}

function ProductTable({ rows }: { rows: ProductStats[] }) {
  return (
    <table>
      <thead>
        <tr>
          <th>商品</th>
          <th>类目</th>
          <th>浏览</th>
          <th>点击</th>
          <th>收藏</th>
          <th>加购</th>
          <th>购买</th>
          <th>转化率</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.productId}>
            <td>{row.productName}</td>
            <td>{row.category}</td>
            <td>{row.browse}</td>
            <td>{row.click}</td>
            <td>{row.favorite}</td>
            <td>{row.cartAdd}</td>
            <td>{row.payment}</td>
            <td>{row.conversionRate}%</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function PieChart({ title, data }: { title: string; data: Record<string, number> }) {
  const entries = Object.entries(data).filter(([, value]) => value > 0).sort((a, b) => b[1] - a[1]).slice(0, 6);
  const total = entries.reduce((sum, [, value]) => sum + value, 0);
  let cursor = 0;
  const slices = entries.map(([label, value], index) => {
    const start = cursor;
    const end = cursor + (value / Math.max(total, 1)) * 100;
    cursor = end;
    return `${pieColors[index % pieColors.length]} ${start}% ${end}%`;
  });
  return (
    <article className="panel pie-card">
      <PanelTitle title={title} meta={total ? `样本 ${total}` : "暂无样本"} />
      <div className="pie-wrap">
        <div className="pie" style={{ background: total ? `conic-gradient(${slices.join(", ")})` : "#edf1f5" }} />
        <div className="pie-legend">
          {entries.length ? entries.map(([label, value], index) => (
            <span key={label}><i style={{ background: pieColors[index % pieColors.length] }} />{label} {value}</span>
          )) : <span>暂无数据</span>}
        </div>
      </div>
    </article>
  );
}

function AlertRow({ alert, withAction = false, canOperate = false }: { alert: AlertItem; withAction?: boolean; canOperate?: boolean }) {
  return (
    <div className="alert-row">
      <strong>{alertTypeLabel(alert.alertType)}</strong>
      <span>{alert.triggerReason}</span>
      <b>{severityLabel(alert.severity)}</b>
      {withAction && <button type="button" disabled={!canOperate}>{canOperate ? "处理" : "无权限"}</button>}
    </div>
  );
}

function PanelTitle({ title, meta }: { title: string; meta: string }) {
  return (
    <div className="panel-title">
      <h2>{title}</h2>
      <span>{meta}</span>
    </div>
  );
}

function EmptyState({ text }: { text: string }) {
  return <div className="empty-state">{text}</div>;
}

function generateProducts() {
  const result: Product[] = [];
  const categoryCounters: Record<string, number> = {};
  for (let i = 0; i < 100; i += 1) {
    const catalog = categoryCatalog[i % categoryCatalog.length];
    const categoryIndex = categoryCounters[catalog.category] ?? 0;
    categoryCounters[catalog.category] = categoryIndex + 1;
    const name = catalog.names[categoryIndex % catalog.names.length];
    const brand = catalog.brands[(categoryIndex + Math.floor(categoryIndex / 3)) % catalog.brands.length];
    const price = catalog.min + ((i * 73) % (catalog.max - catalog.min + 1));
    result.push({
      id: `SKU-${String(i + 1).padStart(3, "0")}`,
      name: `${name} ${String(i + 1).padStart(2, "0")}`,
      brand,
      category: catalog.category,
      price,
      rating: Number((4.3 + ((i * 7) % 7) / 10).toFixed(1)),
      sold: 0,
      stock: 20 + ((i * 41) % 900),
      tag: ["高意向", "热卖", "新品", "复购高", "加购高"][i % 5],
      description: catalog.desc,
      recommendation: `${catalog.category}类目与当前用户近期浏览、收藏或购买行为相似，价格位于该用户常看区间。`,
      image: catalog.image,
    });
  }
  return result;
}

function buildProductSales(events: BehaviorRecord[]) {
  const sales = new Map<string, number>();
  events.forEach((event) => {
    if (readField(event, "eventType", "event_type") !== "payment_success") return;
    const productId = readField(event, "productId", "product_id");
    if (!productId) return;
    sales.set(productId, (sales.get(productId) ?? 0) + saleQuantity(event));
  });
  return sales;
}

function applyProductSales(catalog: Product[], sales: Map<string, number>) {
  return catalog.map((product) => ({ ...product, sold: sales.get(product.id) ?? 0 }));
}

function buildMetricCards(summary: SummaryResponse | null, events: BehaviorRecord[]) {
  const metricValue = (key: string) => summary?.metrics.find((metric) => metric.key === key)?.value ?? 0;
  const visits = metricValue("visits");
  const clicks = metricValue("clicks");
  const carts = metricValue("cart_adds");
  const orders = metricValue("orders");
  const payments = metricValue("payments");
  const sales = events
    .filter((event) => readField(event, "eventType", "event_type") === "payment_success")
    .reduce((sum, event) => sum + productPrice(event), 0);
  const conversion = visits > 0 ? Number(((payments / visits) * 100).toFixed(2)) : 0;
  return [
    { key: "visits", label: "访问量", rawValue: visits, value: visits.toLocaleString(), delta: "实时", tone: "good" },
    { key: "clicks", label: "点击量", rawValue: clicks, value: clicks.toLocaleString(), delta: "实时", tone: "good" },
    { key: "cart_adds", label: "加购量", rawValue: carts, value: carts.toLocaleString(), delta: "实时", tone: "good" },
    { key: "orders", label: "订单量", rawValue: orders, value: orders.toLocaleString(), delta: "实时", tone: "good" },
    { key: "sales", label: "销售额", rawValue: sales, value: `￥${sales.toLocaleString()}`, delta: "支付事件汇总", tone: "good" },
    { key: "payments", label: "转化率", rawValue: payments, value: `${conversion}%`, delta: "支付/访问", tone: conversion > 0 ? "good" : "warn" },
  ];
}

function buildProductStats(events: BehaviorRecord[], catalog: Product[] = products): ProductStats[] {
  const stats = new Map<string, ProductStats>();
  const catalogById = new Map(catalog.map((product) => [product.id, product]));
  catalog.forEach((product) => {
    stats.set(product.id, {
      productId: product.id,
      productName: product.name,
      category: product.category,
      browse: 0,
      click: 0,
      favorite: 0,
      cartAdd: 0,
      order: 0,
      payment: 0,
      conversionRate: 0,
      price: product.price,
    });
  });
  events.forEach((event) => {
    const productId = readField(event, "productId", "product_id");
    if (!productId) return;
    const product = catalogById.get(productId);
    const existing = stats.get(productId) ?? {
      productId,
      productName: productName(event, productId),
      category: productCategory(event, productId),
      browse: 0,
      click: 0,
      favorite: 0,
      cartAdd: 0,
      order: 0,
      payment: 0,
      conversionRate: 0,
      price: product?.price ?? productPrice(event),
    };
    const type = readField(event, "eventType", "event_type");
    if (type === "browse") existing.browse += 1;
    if (type === "click") existing.click += 1;
    if (type === "favorite") existing.favorite += 1;
    if (type === "cart_add") existing.cartAdd += 1;
    if (type === "order_submit") existing.order += 1;
    if (type === "payment_success") existing.payment += 1;
    existing.conversionRate = existing.browse > 0 ? Number(((existing.payment / existing.browse) * 100).toFixed(2)) : 0;
    stats.set(productId, existing);
  });
  return Array.from(stats.values()).sort((left, right) => scoreProductStats(right) - scoreProductStats(left));
}

function buildUserProfiles(events: BehaviorRecord[]): UserProfileStats[] {
  const userIds = ["user001", "user002", "user003"];
  const profiles = new Map<string, UserProfileStats>();
  userIds.forEach((userId) => {
    profiles.set(userId, {
      userId,
      visits: 0,
      clicks: 0,
      favorites: 0,
      carts: 0,
      orders: 0,
      payments: 0,
      paidAmount: 0,
      avgPrice: 0,
      valueLevel: "普通",
      intentLevel: "低",
      segment: "新用户",
      browseCategory: {},
      favoriteCategory: {},
      purchaseCategory: {},
      priceBand: {},
    });
  });
  events.forEach((event) => {
    const userId = getEventUser(event);
    if (!profiles.has(userId)) return;
    const profile = profiles.get(userId)!;
    const type = readField(event, "eventType", "event_type");
    const category = productCategory(event, readField(event, "productId", "product_id"));
    const price = productPrice(event);
    if (type === "browse") {
      profile.visits += 1;
      addCount(profile.browseCategory, category);
      addCount(profile.priceBand, priceBand(price));
    }
    if (type === "click") profile.clicks += 1;
    if (type === "favorite") {
      profile.favorites += 1;
      addCount(profile.favoriteCategory, category);
    }
    if (type === "cart_add") profile.carts += 1;
    if (type === "order_submit") profile.orders += 1;
    if (type === "payment_success") {
      profile.payments += 1;
      profile.paidAmount += price;
      addCount(profile.purchaseCategory, category);
    }
  });
  profiles.forEach((profile) => {
    profile.avgPrice = profile.payments > 0 ? Math.round(profile.paidAmount / profile.payments) : 0;
    const intentScore = profile.visits * 2 + profile.clicks * 4 + profile.favorites * 8 + profile.carts * 15 + profile.orders * 25 + profile.payments * 35;
    profile.intentLevel = intentScore >= 70 ? "高" : intentScore >= 30 ? "中" : "低";
    profile.valueLevel = profile.paidAmount >= 1000 || profile.payments >= 3 ? "高价值" : profile.paidAmount >= 300 || profile.payments >= 1 ? "中价值" : "低价值";
    if (profile.valueLevel === "高价值") profile.segment = "高价值用户";
    else if (profile.carts + profile.favorites >= 3 && profile.payments === 0) profile.segment = "潜力用户";
    else if (profile.visits === 0) profile.segment = "沉默用户";
    else if (profile.avgPrice > 0 && profile.avgPrice <= 250) profile.segment = "价格敏感用户";
    else profile.segment = "新用户";
  });
  return Array.from(profiles.values());
}

function recommendProductsForUser(userId: string, events: BehaviorRecord[], limit: number, catalog: Product[] = products): RecommendationItem[] {
  const relevantEvents = userId === "all" ? events : events.filter((event) => getEventUser(event) === userId);
  const categoryPref: Record<string, number> = {};
  const purchased = new Set<string>();
  let priceTotal = 0;
  let priceSamples = 0;
  relevantEvents.forEach((event) => {
    const type = readField(event, "eventType", "event_type");
    const productId = readField(event, "productId", "product_id");
    const category = productCategory(event, productId);
    const weight = type === "payment_success" ? 8 : type === "cart_add" ? 5 : type === "favorite" ? 4 : type === "click" ? 2 : 1;
    addCount(categoryPref, category, weight);
    if (type === "payment_success") purchased.add(productId);
    if (["browse", "favorite", "cart_add", "payment_success"].includes(type)) {
      priceTotal += productPrice(event);
      priceSamples += 1;
    }
  });
  if (!Object.keys(categoryPref).length && customerSeeds[userId]) {
    customerSeeds[userId].categories.forEach((category, index) => addCount(categoryPref, category, 6 - index));
  }
  const targetPrice = priceSamples ? priceTotal / priceSamples : customerSeeds[userId]?.maxPrice ?? 600;
  return catalog
    .map((product) => {
      const reasons: string[] = [];
      let score = 30;
      if (categoryPref[product.category]) {
        score += Math.min(35, categoryPref[product.category] * 4);
        reasons.push(`偏好类目命中：${product.category}`);
      }
      const priceDistance = Math.abs(product.price - targetPrice);
      if (priceDistance <= targetPrice * 0.35) {
        score += 18;
        reasons.push("价位匹配");
      }
      if (product.sold > 0) {
        score += Math.min(10, product.sold * 2);
        reasons.push("热销商品");
      }
      if (!purchased.has(product.id)) {
        score += 8;
        reasons.push("未购买新商品");
      }
      score += Math.min(8, Math.round((product.rating - 4.2) * 10));
      if (!reasons.length) reasons.push("综合热度靠前");
      return { product, score: Math.min(100, score), reasons };
    })
    .sort((left, right) => right.score - left.score || right.product.sold - left.product.sold)
    .slice(0, limit);
}

function filterEvents(events: BehaviorRecord[], channel: string, keyword: string) {
  return events.filter((event) => {
    const channelId = readField(event, "channelId", "channel_id");
    const productId = readField(event, "productId", "product_id");
    const text = `${productName(event, productId)} ${productId} ${getEventUser(event)} ${readField(event, "searchKeyword", "search_keyword")}`;
    return (channel === "全部渠道" || (channelLabels[channelId] ?? channelId) === channel) && (!keyword.trim() || text.toLowerCase().includes(keyword.trim().toLowerCase()));
  });
}

function readField(record: BehaviorRecord, camel: keyof BehaviorRecord, snake: keyof BehaviorRecord) {
  return String(record[camel] ?? record[snake] ?? "");
}

function getEventUser(event: BehaviorRecord) {
  return readField(event, "userId", "user_id") || readField(event, "visitorId", "visitor_id") || "anonymous";
}

function productName(event: BehaviorRecord, productId: string) {
  return String(event.metadata?.productName ?? productById.get(productId)?.name ?? productId ?? "-");
}

function productCategory(event: BehaviorRecord, productId: string) {
  return String(event.metadata?.category ?? productById.get(productId)?.category ?? "未分类");
}

function productPrice(event: BehaviorRecord) {
  const productId = readField(event, "productId", "product_id");
  return Number(event.metadata?.price ?? productById.get(productId)?.price ?? 0);
}

function saleQuantity(event: BehaviorRecord) {
  const quantity = Number(event.metadata?.quantity ?? 1);
  return Number.isFinite(quantity) && quantity > 0 ? Math.floor(quantity) : 1;
}

function priceBand(price: number) {
  if (price < 100) return "百元内";
  if (price < 300) return "100-299";
  if (price < 600) return "300-599";
  if (price < 1000) return "600-999";
  return "1000+";
}

function scoreProductStats(item: ProductStats) {
  return item.browse + item.click * 1.2 + item.favorite * 1.6 + item.cartAdd * 2 + item.order * 2.8 + item.payment * 4;
}

function addCount(target: Record<string, number>, key: string, value = 1) {
  if (!key) return;
  target[key] = (target[key] ?? 0) + value;
}

function mergeCounts(items: Array<Record<string, number>>) {
  const merged: Record<string, number> = {};
  items.forEach((item) => Object.entries(item).forEach(([key, value]) => addCount(merged, key, value)));
  return merged;
}

function formatTime(value: string) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function formatFreshness(value?: string) {
  if (!value) return "等待数据";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "刚刚";
  return date.toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function maskUser(userId: string) {
  if (!userId) return "-";
  return `${userId.slice(0, 4)}***`;
}

function severityLabel(value: string) {
  return { low: "低", medium: "中", high: "高", critical: "紧急" }[value] ?? value;
}

function alertTypeLabel(value: string) {
  return {
    low_activity: "低活跃提醒",
    churn_risk: "流失风险预警",
    conversion_anomaly: "转化异常预警",
    behavior_data_anomaly: "行为数据异常",
  }[value] ?? value;
}

function reportLabel(value: string) {
  return {
    behavior_detail: "用户行为明细",
    product_analysis: "商品分析报表",
    funnel: "转化漏斗报表",
    user_profile: "用户画像报表",
    user_segment: "用户分群报表",
    sales_conversion: "销售转化报表",
    operation_effect: "运营效果报表",
  }[value] ?? value;
}

export default App;
