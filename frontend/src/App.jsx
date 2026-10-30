
import { useCallback, useEffect, useMemo, useState } from "react";
import "./App.css";
import farmGoldenHour from "./assets/images/farm-golden-hour.png";
import cropImage from "./assets/images/crop-image.jpg";
import fertilizerImage from "./assets/images/fertilizer-image.jpg";
import dashboardImage from "./assets/images/dashboard-image.jpg";
const API = (import.meta.env.VITE_API_URL || "/api").replace(/\/$/, "");

const INITIAL_FARM = {
  N: 90,
  P: 42,
  K: 43,
  temperature: 26.5,
  humidity: 75,
  ph: 6.5,
  rainfall: 180,
  moisture: 40,
  soil_type: "Loamy",
  area: "India",
  year: 2013,
  pesticides: 12,
  crop: "rice",
  fertilizer_crop: "rice",
  trend_crop: "rice",
};

const CROP_MODEL_CROPS = [
  ["apple", "Apple"],
  ["banana", "Banana"],
  ["blackgram", "Blackgram"],
  ["chickpea", "Chickpea"],
  ["coconut", "Coconut"],
  ["coffee", "Coffee"],
  ["cotton", "Cotton"],
  ["grapes", "Grapes"],
  ["jute", "Jute"],
  ["kidneybeans", "Kidney beans"],
  ["lentil", "Lentil"],
  ["maize", "Maize"],
  ["mango", "Mango"],
  ["mothbeans", "Moth beans"],
  ["mungbean", "Mung bean"],
  ["muskmelon", "Muskmelon"],
  ["orange", "Orange"],
  ["papaya", "Papaya"],
  ["pigeonpeas", "Pigeon peas"],
  ["pomegranate", "Pomegranate"],
  ["rice", "Rice"],
  ["watermelon", "Watermelon"],
];

const FERTILIZER_CROP_OPTIONS = [
  ...CROP_MODEL_CROPS,
  ["wheat", "Wheat"],
  ["sugarcane", "Sugarcane"],
  ["barley", "Barley"],
  ["millets", "Millets"],
  ["groundnuts", "Groundnuts"],
  ["oilseeds", "Oilseeds"],
  ["tobacco", "Tobacco"],
  ["pulses", "Pulses"],
];

const YIELD_CROP_OPTIONS = [
  ["rice", "Rice"],
  ["maize", "Maize"],
  ["wheat", "Wheat"],
  ["banana", "Banana"],
  ["cassava", "Cassava"],
  ["potatoes", "Potatoes"],
  ["sorghum", "Sorghum"],
  ["soybeans", "Soybeans"],
  ["sweet potatoes", "Sweet potatoes"],
  ["yams", "Yams"],
  ["plantains and others", "Plantains and others"],
];

const CROP_LABELS = Object.fromEntries([
  ...CROP_MODEL_CROPS,
  ...FERTILIZER_CROP_OPTIONS,
  ...YIELD_CROP_OPTIONS,
]);

const SOILS = ["Loamy", "Clayey", "Sandy", "Black", "Red"];

const TEXT = {
  en: {
    workspace: "WORKSPACE",
    overview: "Dashboard",
    cropAdvisor: "Crop advisor",
    cropRecommendation: "Crop recommendation",
    fertilizer: "Fertilizer advisor",
    yield: "Yield insights",
    assistant: "AI assistant",
    fieldTip: "Better decisions start with better field data.",
    explore: "Explore recommendations",
    profile: "Farm workspace",
    subtitle: "SMART AGRICULTURE PLATFORM",
    greeting: "Grow smarter.",
    greeting2: "Farm better.",
    heroDescription:
      "Bring your soil data, crop recommendations, yield insights, and AI assistance together in one place.",
    getStarted: "Generate recommendations",
    dashboard: "Dashboard",
    overviewTitle: "Your farm at a glance",
    overviewDescription:
      "Review your field conditions and the latest recommendation results.",
    cropMetric: "Recommended crop",
    fertilizerMetric: "Fertilizer",
    yieldMetric: "Latest historical yield",
    soilMetric: "Soil pH",
    waiting: "Waiting for farm data",
    latestResult: "From your latest model result",
    modelEstimate: "Model estimate, not a guarantee",
    currentConditions: "Current field conditions",
    conditionsDescription: "Values from your farm input form",
    temperature: "Temperature",
    humidity: "Humidity",
    rainfall: "Rainfall",
    soilType: "Soil type",
    quickActions: "Quick actions",
    quickDescription: "Continue with a farm task",
    openCrop: "Explore crop recommendations",
    openFertilizer: "Plan fertilizer",
    openYield: "View historical yield",
    assistantAction: "Ask the AI assistant",
    cropHeading: "Find a suitable crop",
    cropDescription:
      "Enter your soil nutrients and environmental conditions to run the crop classifier. This page does not predict fertilizer or yield.",
    fertilizerHeading: "Fertilizer guidance for a selected crop",
    fertilizerDescription:
      "Select the crop you plan to grow, then enter its soil and weather measurements. Results are a fertilizer category only, not a dosage.",
    yieldHeading: "Historical crop yield",
    yieldDescription:
      "Explore historical yield records available in your dataset.",
    assistantHeading: "Your agricultural AI assistant",
    assistantDescription:
      "Ask practical questions about crop selection, soil health, fertilizer planning, or farming.",
    farmInputs: "Farm inputs",
    farmInputsDescription: "Enter the available measurements for your field.",
    generate: "Generate recommendations",
    analyzing: "Analyzing your farm…",
    runAgain: "Refresh recommendation",
    soilNutrients: "SOIL NUTRIENTS",
    weatherConditions: "WEATHER CONDITIONS",
    farmDetails: "FARM DETAILS",
    nitrogen: "Nitrogen (N)",
    phosphorus: "Phosphorus (P)",
    potassium: "Potassium (K)",
    ph: "Soil pH",
    moisture: "Soil moisture",
    area: "Country / area",
    year: "Prediction year",
    pesticides: "Pesticide usage",
    crop: "Crop",
    result: "Recommendation results",
    resultDescription: "Results returned by your connected backend.",
    cropResult: "Crop recommendation",
    fertilizerResult: "Fertilizer result",
    noResult: "Your results will appear here",
    noResultDescription:
      "Complete the fields and generate a result to see the model output.",
    noCropResult: "Enter soil and weather values to recommend a crop.",
    noFertilizerResult:
      "Select a crop and enter its measurements to request fertilizer guidance.",
    confidence: "Model confidence",
    suitability: "Top crop suitability scores",
    prescription: "AI farming guidance",
    recommendedCrop: "Recommended crop",
    recommendedFertilizer: "Recommended fertilizer",
    predictedYield: "Predicted yield",
    explanation: "Explanation",
    warnings: "Input warnings",
    guidance: "Guidance",
    limitations: "Limitations",
    selectedCrop: "Selected crop",
    cropCategory: "Dataset crop category",
    fertilizerCrop: "Crop for fertilizer guidance",
    cropHandoff: "Crop selected from your crop recommendation.",
    getFertilizer: "Get fertilizer guidance",
    fertilizerBelow:
      "Fertilizer guidance for this crop is shown in the section below.",
    runCrop: "Recommend a crop",
    runFertilizer: "Get fertilizer guidance",
    analyzingCrop: "Analyzing soil and weather…",
    analyzingFertilizer: "Matching fertilizer guidance…",
    supportedCrops: "Supported fertilizer crop categories",
    unsupportedCrop: "Fertilizer guidance is unavailable for this crop.",
    noDosage:
      "No fertilizer quantity or application schedule is shown because the bundled dataset does not contain that information.",
    dataQuality: "Data quality",
    historicalYieldNote:
      "Latest record in the historical dataset, not a prediction.",
    useCarefully: "Use recommendations responsibly",
    safetyText:
      "Validate soil measurements and crop advice with local agricultural experts. The fertilizer result is a category only; confirm dosage and timing separately.",
    history: "Historical yield trend",
    historyNote:
      "Values are taken from the configured historical dataset, not generated by the AI.",
    historicalSource: "Source",
    historicalUnit: "Yield",
    refresh: "Refresh data",
    loadingHistory: "Loading historical records…",
    noHistory: "No matching historical records were found.",
    chooseCrop: "Choose a crop",
    chooseArea: "Choose an area",
    yearRange: "Historical period: 1993–2013",
    sourceDataset: "Historical dataset",
    assistantOnline: "Connected through your configured AI service",
    online: "Ready",
    offline: "Connection issue",
    typeQuestion: "Ask a farming question…",
    send: "Send",
    thinking: "Preparing an answer…",
    suggestions: "TRY ASKING",
    prompt1: "How can I improve soil health?",
    prompt2: "Explain NPK nutrients",
    prompt3: "How should I plan fertilizer?",
    disclaimer:
      "AI responses can be incorrect. Verify important agricultural decisions locally.",
    welcome:
      "Hello! I’m AgroAgent. Ask me about crop selection, soil health, fertilizer planning, or improving your harvest.",
    footer:
      "AgroAgent · Smart agricultural decision support",
    language: "Language",
    english: "English",
    tamil: "தமிழ்",
    today: "Farm overview",
    error: "Something went wrong",
    dismiss: "Dismiss",
    backendError:
      "Could not connect to the backend. Make sure the Django server is running.",
    noCropHistory:
      "No matching records for this crop and area. Try Rice, Maize, or Wheat for India.",
  },
  ta: {
    workspace: "பணித்தளம்",
    overview: "முகப்புப் பலகை",
    cropAdvisor: "பயிர் ஆலோசகர்",
    cropRecommendation: "பயிர் பரிந்துரை",
    fertilizer: "உர ஆலோசகர்",
    yield: "மகசூல் விவரங்கள்",
    assistant: "AI உதவியாளர்",
    fieldTip: "சரியான வயல் தகவல்கள் சிறந்த முடிவுகளுக்கு உதவும்.",
    explore: "பரிந்துரைகளைப் பார்க்க",
    profile: "பண்ணை பணித்தளம்",
    subtitle: "நவீன விவசாயத் தளம்",
    greeting: "அறிவுடன் பயிரிடுங்கள்.",
    greeting2: "சிறப்பாக விளைவியுங்கள்.",
    heroDescription:
      "மண் தகவல்கள், பயிர் பரிந்துரைகள், மகசூல் விவரங்கள் மற்றும் AI உதவியை ஒரே இடத்தில் பெறுங்கள்.",
    getStarted: "பரிந்துரைகளை உருவாக்கு",
    dashboard: "முகப்புப் பலகை",
    overviewTitle: "உங்கள் பண்ணையின் நிலை",
    overviewDescription:
      "வயல் நிலைமைகளையும் சமீபத்திய பரிந்துரைகளையும் பாருங்கள்.",
    cropMetric: "பரிந்துரைக்கப்பட்ட பயிர்",
    fertilizerMetric: "உரம்",
    yieldMetric: "சமீபத்திய வரலாற்று மகசூல்",
    soilMetric: "மண் pH",
    waiting: "பண்ணைத் தகவல்களுக்காக காத்திருக்கிறது",
    latestResult: "சமீபத்திய மாதிரி முடிவு",
    modelEstimate: "மாதிரிக் கணிப்பு; உறுதியான பலன் அல்ல",
    currentConditions: "தற்போதைய வயல் நிலைமைகள்",
    conditionsDescription: "உங்கள் படிவத்தில் உள்ள மதிப்புகள்",
    temperature: "வெப்பநிலை",
    humidity: "ஈரப்பதம்",
    rainfall: "மழைப்பொழிவு",
    soilType: "மண் வகை",
    quickActions: "விரைவு செயல்கள்",
    quickDescription: "விவசாயப் பணியைத் தேர்ந்தெடுக்கவும்",
    openCrop: "பயிர் பரிந்துரைகளைப் பார்க்க",
    openFertilizer: "உரத் திட்டம்",
    openYield: "வரலாற்று மகசூலைப் பார்க்க",
    assistantAction: "AI உதவியாளரிடம் கேளுங்கள்",
    cropHeading: "பொருத்தமான பயிரைக் கண்டறியுங்கள்",
    cropDescription:
      "பயிர் வகைப்படுத்தியை இயக்க மண் மற்றும் சுற்றுச்சூழல் மதிப்புகளை உள்ளிடுங்கள். இந்தப் பக்கம் உரம் அல்லது மகசூலைக் கணிக்காது.",
    fertilizerHeading: "தேர்ந்தெடுத்த பயிருக்கான உர வழிகாட்டுதல்",
    fertilizerDescription:
      "நீங்கள் பயிரிடப்போகும் பயிரைத் தேர்ந்தெடுத்து, மண் மற்றும் வானிலை அளவீடுகளை உள்ளிடுங்கள். முடிவு உர வகை மட்டுமே; அளவு அல்ல.",
    yieldHeading: "வரலாற்று பயிர் மகசூல்",
    yieldDescription:
      "தரவுத்தொகுப்பில் உள்ள வரலாற்று மகசூல் பதிவுகளைப் பாருங்கள்.",
    assistantHeading: "உங்கள் விவசாய AI உதவியாளர்",
    assistantDescription:
      "பயிர் தேர்வு, மண் வளம், உரத் திட்டம் மற்றும் விவசாயம் பற்றி கேளுங்கள்.",
    farmInputs: "வயல் தகவல்கள்",
    farmInputsDescription: "உங்கள் வயலுக்குக் கிடைக்கும் அளவீடுகளை உள்ளிடுங்கள்.",
    generate: "பரிந்துரைகளை உருவாக்கு",
    analyzing: "வயல் தகவல்கள் பகுப்பாய்வு செய்யப்படுகின்றன…",
    runAgain: "மீண்டும் கணக்கிடு",
    soilNutrients: "மண் ஊட்டச்சத்துகள்",
    weatherConditions: "வானிலை நிலைமைகள்",
    farmDetails: "பண்ணை விவரங்கள்",
    nitrogen: "நைட்ரஜன் (N)",
    phosphorus: "பாஸ்பரஸ் (P)",
    potassium: "பொட்டாசியம் (K)",
    ph: "மண் pH",
    moisture: "மண் ஈரப்பதம்",
    area: "நாடு / பகுதி",
    year: "கணிப்பு ஆண்டு",
    pesticides: "பூச்சிக்கொல்லி பயன்பாடு",
    crop: "பயிர்",
    result: "பரிந்துரை முடிவுகள்",
    resultDescription: "உங்கள் இணைக்கப்பட்ட backend வழங்கிய முடிவுகள்.",
    cropResult: "பயிர் பரிந்துரை",
    fertilizerResult: "உர முடிவு",
    noResult: "முடிவுகள் இங்கே தோன்றும்",
    noResultDescription:
      "புலங்களை நிரப்பி முடிவை உருவாக்குங்கள்.",
    noCropResult:
      "பயிர் பரிந்துரைக்க மண் மற்றும் வானிலை மதிப்புகளை உள்ளிடுங்கள்.",
    noFertilizerResult:
      "உர வழிகாட்டுதலைப் பெற பயிரைத் தேர்ந்தெடுத்து அளவீடுகளை உள்ளிடுங்கள்.",
    confidence: "மாதிரி நம்பகத்தன்மை",
    suitability: "சிறந்த பயிர்களின் பொருத்த மதிப்புகள்",
    prescription: "AI விவசாய வழிகாட்டுதல்",
    recommendedCrop: "பரிந்துரைக்கப்பட்ட பயிர்",
    recommendedFertilizer: "பரிந்துரைக்கப்பட்ட உரம்",
    predictedYield: "கணிக்கப்பட்ட மகசூல்",
    explanation: "விளக்கம்",
    warnings: "உள்ளீட்டு எச்சரிக்கைகள்",
    guidance: "வழிகாட்டுதல்",
    limitations: "வரம்புகள்",
    selectedCrop: "தேர்ந்தெடுத்த பயிர்",
    cropCategory: "தரவுத்தொகுப்பு பயிர் வகை",
    fertilizerCrop: "உர வழிகாட்டுதலுக்கான பயிர்",
    cropHandoff: "உங்கள் பயிர் பரிந்துரையிலிருந்து தேர்ந்தெடுக்கப்பட்ட பயிர்.",
    getFertilizer: "உர வழிகாட்டுதலைப் பெறுங்கள்",
    fertilizerBelow:
      "இந்தப் பயிருக்கான உர வழிகாட்டுதல் கீழே உள்ள பகுதியில் காட்டப்படுகிறது.",
    runCrop: "பயிரைப் பரிந்துரைக்கவும்",
    runFertilizer: "உர வழிகாட்டுதலைப் பெறுங்கள்",
    analyzingCrop: "மண் மற்றும் வானிலை பகுப்பாய்வு செய்யப்படுகிறது…",
    analyzingFertilizer: "உர வழிகாட்டுதல் பொருத்தப்படுகிறது…",
    supportedCrops: "ஆதரிக்கப்படும் உர பயிர் வகைகள்",
    unsupportedCrop: "இந்தப் பயிருக்கு உர வழிகாட்டுதல் கிடைக்கவில்லை.",
    noDosage:
      "தரவுத்தொகுப்பில் அந்தத் தகவல் இல்லாததால் உர அளவு அல்லது பயன்பாட்டு நேரம் காட்டப்படவில்லை.",
    dataQuality: "தரவுத் தரம்",
    historicalYieldNote:
      "வரலாற்றுத் தரவுத்தொகுப்பின் சமீபத்திய பதிவு; கணிப்பு அல்ல.",
    useCarefully: "பரிந்துரைகளைச் சரிபார்த்துப் பயன்படுத்துங்கள்",
    safetyText:
      "மண் அளவீடுகளையும் பயிர் ஆலோசனையையும் உள்ளூர் வேளாண் நிபுணர்களிடம் சரிபார்க்கவும். உர முடிவு ஒரு வகை மட்டுமே; அளவையும் நேரத்தையும் தனியாக உறுதிப்படுத்தவும்.",
    history: "வரலாற்று மகசூல் போக்கு",
    historyNote:
      "இந்த மதிப்புகள் வரலாற்றுத் தரவுத்தொகுப்பிலிருந்து பெறப்படுகின்றன; AI உருவாக்கியவை அல்ல.",
    historicalSource: "தரவு மூலம்",
    historicalUnit: "மகசூல்",
    refresh: "தரவைப் புதுப்பி",
    loadingHistory: "வரலாற்றுப் பதிவுகள் ஏற்றப்படுகின்றன…",
    noHistory: "பொருந்தும் வரலாற்றுப் பதிவுகள் கிடைக்கவில்லை.",
    chooseCrop: "பயிரைத் தேர்ந்தெடுக்கவும்",
    chooseArea: "பகுதியைத் தேர்ந்தெடுக்கவும்",
    yearRange: "வரலாற்றுக் காலம்: 1993–2013",
    sourceDataset: "வரலாற்றுத் தரவுத்தொகுப்பு",
    assistantOnline: "உங்கள் AI சேவையுடன் இணைக்கப்பட்டுள்ளது",
    online: "தயார்",
    offline: "இணைப்புச் சிக்கல்",
    typeQuestion: "விவசாயக் கேள்வியைக் கேளுங்கள்…",
    send: "அனுப்பு",
    thinking: "பதில் தயாராகிறது…",
    suggestions: "இவற்றைக் கேளுங்கள்",
    prompt1: "மண் வளத்தை எவ்வாறு மேம்படுத்தலாம்?",
    prompt2: "NPK ஊட்டச்சத்துகளை விளக்குங்கள்",
    prompt3: "உரத்தை எப்படித் திட்டமிடலாம்?",
    disclaimer:
      "AI பதில்களில் தவறுகள் இருக்கலாம். முக்கிய முடிவுகளை உள்ளூரில் சரிபார்க்கவும்.",
    welcome:
      "வணக்கம்! நான் AgroAgent. பயிர் தேர்வு, மண் வளம், உரத் திட்டம் அல்லது மகசூல் மேம்பாடு பற்றி கேளுங்கள்.",
    footer: "AgroAgent · நவீன விவசாய முடிவு உதவி",
    language: "மொழி",
    english: "English",
    tamil: "தமிழ்",
    today: "பண்ணை நிலை",
    error: "சிக்கல் ஏற்பட்டது",
    dismiss: "மூடு",
    backendError:
      "Backend-ஐ இணைக்க முடியவில்லை. Django server இயங்குகிறதா எனப் பாருங்கள்.",
    noCropHistory:
      "இந்தப் பயிருக்கும் பகுதிக்கும் பதிவுகள் இல்லை. இந்தியாவிற்கு Rice, Maize அல்லது Wheat முயற்சிக்கவும்.",
  },
};

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...options.headers,
    },
  });

  let data = {};
  try {
    data = await response.json();
  } catch {
    data = {};
  }

  if (!response.ok) {
    const message =
      data.message ||
      data.error ||
      data.detail ||
      `Request failed (${response.status})`;

    throw new Error(message);
  }

  return data;
}

function Icon({ name, size = 22, strokeWidth = 1.8, className = "" }) {
  const common = {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth,
    strokeLinecap: "round",
    strokeLinejoin: "round",
    className,
    "aria-hidden": true,
  };

  const paths = {
    leaf: (
      <>
        <path d="M20.5 3.5C11 3.5 5 6.5 5 13a5 5 0 0 0 5 5c6.5 0 9.5-6 10.5-14.5Z" />
        <path d="M3 21c3.5-6 7.5-9 13-12" />
      </>
    ),
    grid: (
      <>
        <rect x="3" y="3" width="7" height="7" rx="1.5" />
        <rect x="14" y="3" width="7" height="7" rx="1.5" />
        <rect x="3" y="14" width="7" height="7" rx="1.5" />
        <rect x="14" y="14" width="7" height="7" rx="1.5" />
      </>
    ),
    sprout: (
      <>
        <path d="M12 21v-9" />
        <path d="M12 12C12 6 7 4 3 5c0 5 3 9 9 7Z" />
        <path d="M12 16c0-6 5-9 9-8 0 5-3 9-9 8Z" />
      </>
    ),
    flask: (
      <>
        <path d="M9 3h6" />
        <path d="M10 3v6l-5.5 9.2A2 2 0 0 0 6.2 21h11.6a2 2 0 0 0 1.7-2.8L14 9V3" />
        <path d="M8 15h8" />
      </>
    ),
    chart: (
      <>
        <path d="M3 3v18h18" />
        <path d="m7 14 4-4 4 3 5-7" />
        <path d="M16 6h4v4" />
      </>
    ),
    chat: (
      <>
        <path d="M21 11.5a7.5 7.5 0 0 1-7.5 7.5H7l-4 2v-6.5A7.5 7.5 0 1 1 21 11.5Z" />
        <path d="M8 11h8M8 14h5" />
      </>
    ),
    sun: (
      <>
        <circle cx="12" cy="12" r="4" />
        <path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32 1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
      </>
    ),
    water: (
      <>
        <path d="M12 3C9 7 5 11 5 15a7 7 0 0 0 14 0c0-4-4-8-7-12Z" />
        <path d="M9 16a3 3 0 0 0 3 3" />
      </>
    ),
    arrow: <path d="M5 12h14m-6-6 6 6-6 6" />,
    sparkle: (
      <>
        <path d="m12 3 1.9 5.8L20 11l-6.1 2.2L12 19l-1.9-5.8L4 11l6.1-2.2L12 3Z" />
        <path d="m19 14 1.1 2.4L22 17l-1.9.7L19 20l-.8-2.3L16 17l2.2-.6L19 14Z" />
      </>
    ),
    calendar: (
      <>
        <rect x="3" y="5" width="18" height="16" rx="2" />
        <path d="M16 3v4M8 3v4M3 10h18" />
      </>
    ),
    menu: (
      <>
        <path d="M4 6h16M4 12h16M4 18h16" />
      </>
    ),
    close: <path d="m6 6 12 12M18 6 6 18" />,
    check: <path d="m5 12 4 4L19 6" />,
    activity: (
      <>
        <path d="M3 12h4l3-8 4 16 3-8h4" />
      </>
    ),
    globe: (
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18" />
      </>
    ),
    send: (
      <>
        <path d="m22 2-7 20-4-9-9-4 20-7Z" />
        <path d="M22 2 11 13" />
      </>
    ),
    alert: (
      <>
        <path d="M12 3 2.8 20h18.4L12 3Z" />
        <path d="M12 9v4m0 3h.01" />
      </>
    ),
  };

  return <svg {...common}>{paths[name] || paths.leaf}</svg>;
}

function SectionTitle({ eyebrow, title, description, action }) {
  return (
    <div className="section-title">
      <div>
        {eyebrow && <p className="eyebrow">{eyebrow}</p>}
        <h2>{title}</h2>
        {description && <p className="muted">{description}</p>}
      </div>
      {action}
    </div>
  );
}

function Metric({ icon, label, value, note, color = "green" }) {
  return (
    <article className="metric-card">
      <div className={`metric-icon ${color}`}>
        <Icon name={icon} size={23} />
      </div>
      <p className="metric-label">{label}</p>
      <h3 title={String(value)}>{value}</h3>
      <p className="metric-note">{note}</p>
    </article>
  );
}

function CropForm({ farm, setFarm, onSubmit, loading, t }) {
  const update = (key, value) => {
    setFarm((previous) => ({ ...previous, [key]: value }));
  };

  const numericField = (key, label, unit, min, max, step = "any") => (
    <label className="field" key={key}>
      <span>{label}</span>
      <div className="input-unit">
        <input
          type="number"
          name={key}
          value={farm[key]}
          min={min}
          max={max}
          step={step}
          required
          onChange={(event) => update(key, event.target.value)}
        />
        {unit && <small>{unit}</small>}
      </div>
    </label>
  );

  return (
    <form className="farm-form" onSubmit={onSubmit}>
      <div>
        <div className="form-heading">
          <div className="metric-icon green">
            <Icon name="leaf" />
          </div>
          <div>
            <h3>{t("soilNutrients")}</h3>
            <p>{t("farmInputsDescription")}</p>
          </div>
        </div>
        <div className="form-grid">
          {numericField("N", t("nitrogen"), "mg/kg", 0, 500)}
          {numericField("P", t("phosphorus"), "mg/kg", 0, 500)}
          {numericField("K", t("potassium"), "mg/kg", 0, 500)}
          {numericField("ph", t("ph"), "pH", 0, 14, 0.1)}
        </div>
      </div>

      <div>
        <div className="form-heading">
          <div className="metric-icon blue">
            <Icon name="sun" />
          </div>
          <div>
            <h3>{t("weatherConditions")}</h3>
            <p>{t("conditionsDescription")}</p>
          </div>
        </div>
        <div className="form-grid">
          {numericField("temperature", t("temperature"), "°C", -10, 60)}
          {numericField("humidity", t("humidity"), "%", 0, 100)}
          {numericField("rainfall", t("rainfall"), "mm", 0, 10000)}
        </div>
      </div>

      <p className="form-footnote">{t("cropDescription")}</p>
      <p className="form-footnote">
        Example values are prefilled. Replace them with your field measurements
        before running the model.
      </p>

      <button className="button button-primary button-full" disabled={loading}>
        <Icon name={loading ? "activity" : "sparkle"} size={19} />
        {loading ? t("analyzingCrop") : t("runCrop")}
        {!loading && <Icon name="arrow" size={18} />}
      </button>
    </form>
  );
}

function FertilizerForm({
  farm,
  setFarm,
  onSubmit,
  loading,
  t,
  cropCarried,
  clearCropCarried,
}) {
  const update = (key, value) => {
    setFarm((previous) => ({ ...previous, [key]: value }));
  };

  const numericField = (key, label, unit, min, max, step = "any") => (
    <label className="field" key={key}>
      <span>{label}</span>
      <div className="input-unit">
        <input
          type="number"
          name={key}
          value={farm[key]}
          min={min}
          max={max}
          step={step}
          required
          onChange={(event) => update(key, event.target.value)}
        />
        {unit && <small>{unit}</small>}
      </div>
    </label>
  );

  return (
    <form className="farm-form" onSubmit={onSubmit}>
      {cropCarried && (
        <div className="info-banner">
          <Icon name="check" size={19} />
          <p>
            <strong>{t("cropHandoff")}</strong> {cropCarried}
          </p>
        </div>
      )}

      <label className="field">
        <span>{t("fertilizerCrop")}</span>
        <select
          value={farm.fertilizer_crop}
          onChange={(event) => {
            update("fertilizer_crop", event.target.value);
            if (cropCarried) clearCropCarried();
          }}
          required
        >
          {FERTILIZER_CROP_OPTIONS.map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </label>

      <div>
        <div className="form-heading">
          <div className="metric-icon green">
            <Icon name="leaf" />
          </div>
          <div>
            <h3>{t("soilNutrients")}</h3>
            <p>{t("farmInputsDescription")}</p>
          </div>
        </div>
        <div className="form-grid">
          {numericField("N", t("nitrogen"), "mg/kg", 0, 500)}
          {numericField("P", t("phosphorus"), "mg/kg", 0, 500)}
          {numericField("K", t("potassium"), "mg/kg", 0, 500)}
          {numericField("moisture", t("moisture"), "%", 0, 100)}
          <label className="field">
            <span>{t("soilType")}</span>
            <select
              value={farm.soil_type}
              onChange={(event) => update("soil_type", event.target.value)}
              required
            >
              {SOILS.map((soil) => (
                <option key={soil} value={soil}>
                  {soil}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      <div>
        <div className="form-heading">
          <div className="metric-icon blue">
            <Icon name="sun" />
          </div>
          <div>
            <h3>{t("weatherConditions")}</h3>
            <p>{t("conditionsDescription")}</p>
          </div>
        </div>
        <div className="form-grid">
          {numericField("temperature", t("temperature"), "°C", -10, 60)}
          {numericField("humidity", t("humidity"), "%", 0, 100)}
        </div>
      </div>

      <p className="form-footnote">{t("fertilizerDescription")}</p>

      <button className="button button-primary button-full" disabled={loading}>
        <Icon name={loading ? "activity" : "flask"} size={19} />
        {loading ? t("analyzingFertilizer") : t("runFertilizer")}
        {!loading && <Icon name="arrow" size={18} />}
      </button>
    </form>
  );
}

function TrendChart({ records, t }) {
  const chart = useMemo(() => {
    if (!records.length) return null;

    const values = records.map((record) => Number(record.yield));
    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = max - min || 1;
    const width = 760;
    const height = 280;
    const left = 44;
    const right = 18;
    const top = 22;
    const bottom = 38;
    const plotWidth = width - left - right;
    const plotHeight = height - top - bottom;

    const points = records.map((record, index) => ({
      x:
        left +
        (records.length === 1 ? plotWidth / 2 : (index / (records.length - 1)) * plotWidth),
      y: top + plotHeight - ((Number(record.yield) - min) / range) * plotHeight,
      year: record.year,
      yield: Number(record.yield),
    }));

    return {
      width,
      height,
      points,
      min,
      max,
      line: points.map((point) => `${point.x},${point.y}`).join(" "),
      labels: [
        records[0].year,
        records[Math.floor((records.length - 1) / 2)].year,
        records[records.length - 1].year,
      ],
    };
  }, [records]);

  if (!chart) return null;

  const gridY = [0, 1, 2, 3].map(
    (step) => 22 + step * ((280 - 22 - 38) / 3)
  );

  return (
    <div className="trend-visual">
      <svg
        viewBox={`0 0 ${chart.width} ${chart.height}`}
        role="img"
        aria-label={t("history")}
      >
        <defs>
          <linearGradient id="yieldArea" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="#4c9161" stopOpacity=".23" />
            <stop offset="100%" stopColor="#4c9161" stopOpacity="0" />
          </linearGradient>
        </defs>

        {gridY.map((y) => (
          <line
            key={y}
            x1="44"
            x2="742"
            y1={y}
            y2={y}
            className="chart-gridline"
          />
        ))}

        <polygon
          points={`44,242 ${chart.line} 742,242`}
          fill="url(#yieldArea)"
        />
        <polyline points={chart.line} className="chart-line" />

        {chart.points.map((point) => (
          <g key={point.year}>
            <circle
              cx={point.x}
              cy={point.y}
              r="4"
              className="chart-point"
            >
              <title>
                {point.year}: {point.yield.toFixed(2)} tonnes/ha
              </title>
            </circle>
          </g>
        ))}

        {chart.labels.map((year, index) => {
          const x = [44, 393, 742][index];
          return (
            <text
              key={`${year}-${index}`}
              x={x}
              y="269"
              fill="#77877a"
              fontSize="13"
              textAnchor={index === 0 ? "start" : index === 2 ? "end" : "middle"}
            >
              {year}
            </text>
          );
        })}
      </svg>
    </div>
  );
}

function ResultMessage({ icon, title, description, loading = false }) {
  return (
    <div className="empty-result">
      {loading ? (
        <div className="loading-line" />
      ) : (
        <div className="result-symbol">
          <Icon name={icon} size={28} />
        </div>
      )}
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}

function WarningList({ warnings, t }) {
  if (!Array.isArray(warnings) || warnings.length === 0) return null;

  return (
    <div className="warning-block">
      <h4>{t("warnings")}</h4>
      <ul className="warning-list">
        {warnings.map((warning) => (
          <li key={warning}>
            <Icon name="alert" size={15} />
            <span>{warning}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function SupportList({ categories, t }) {
  if (!Array.isArray(categories) || categories.length === 0) return null;

  return (
    <div className="support-block">
      <h4>{t("supportedCrops")}</h4>
      <div className="support-list">
        {categories.map((category) => (
          <span key={category}>{category}</span>
        ))}
      </div>
    </div>
  );
}

function CropResultPanel({
  result,
  loading,
  error,
  t,
}) {
  if (loading) {
    return (
      <ResultMessage
        icon="activity"
        title={t("analyzingCrop")}
        description="Running the crop classifier with your soil and weather values."
        loading
        t={t}
      />
    );
  }

  if (error) {
    return (
      <ResultMessage
        icon="alert"
        title={t("error")}
        description={error}
        t={t}
      />
    );
  }

  if (!result) {
    return (
      <ResultMessage
        icon="sprout"
        title={t("noResult")}
        description={t("noCropResult")}
        t={t}
      />
    );
  }

  const confidence = Number(result.confidence);
  const suitability = Array.isArray(result.suitability)
    ? result.suitability.slice(0, 5)
    : [];

  return (
    <div className="result-content">
      <div className="result-title">
        <div className="result-symbol">
          <Icon name="check" size={24} />
        </div>
        <div>
          <p className="eyebrow">{t("cropResult")}</p>
          <h3>{result.crop || "—"}</h3>
        </div>
        {Number.isFinite(confidence) && (
          <span className="confidence">
            {confidence.toFixed(1)}% {t("confidence")}
          </span>
        )}
      </div>

      <WarningList warnings={result.warnings} t={t} />

      {result.explanation && (
        <div className="prescription">
          <strong>
            <Icon name="activity" size={17} />
            {t("explanation")}
          </strong>
          <p>{result.explanation}</p>
        </div>
      )}

      {suitability.length > 0 && (
        <div className="suitability">
          <h4>{t("suitability")}</h4>
          {suitability.map((item) => {
            const score = Math.max(
              0,
              Math.min(100, Number(item.prob || 0) * 100)
            );
            return (
              <div className="score-row" key={item.crop}>
                <span>{item.crop}</span>
                <div className="score-track">
                  <div style={{ width: `${score}%` }} />
                </div>
                <small>{score.toFixed(1)}%</small>
              </div>
            );
          })}
        </div>
      )}

      {result.prescription && (
        <div className="prescription">
          <strong>
            <Icon name="sparkle" size={17} />
            {t("prescription")}
          </strong>
          <p>{result.prescription}</p>
        </div>
      )}

      {result.fertilizer_supported ? (
        <p className="result-hint">
          <Icon name="flask" size={17} />
          <span>{t("fertilizerBelow")}</span>
        </p>
      ) : (
        <p className="limitation-note">{t("unsupportedCrop")}</p>
      )}

      {result.caveat && (
        <p className="limitation-note">{result.caveat}</p>
      )}
    </div>
  );
}

function FertilizerResultPanel({ result, loading, error, t }) {
  if (loading) {
    return (
      <ResultMessage
        icon="flask"
        title={t("analyzingFertilizer")}
        description="Matching the selected crop and soil measurements to a fertilizer category."
        loading
        t={t}
      />
    );
  }

  if (error) {
    return (
      <ResultMessage
        icon="alert"
        title={t("error")}
        description={error}
        t={t}
      />
    );
  }

  if (!result) {
    return (
      <ResultMessage
        icon="flask"
        title={t("noResult")}
        description={t("noFertilizerResult")}
        t={t}
      />
    );
  }

  if (result.supported === false) {
    return (
      <div className="result-content">
        <div className="result-title">
          <div className="result-symbol">
            <Icon name="alert" size={24} />
          </div>
          <div>
            <p className="eyebrow">{t("fertilizerResult")}</p>
            <h3>{t("unsupportedCrop")}</h3>
          </div>
        </div>
        <p className="form-footnote">{result.message}</p>
        <SupportList categories={result.supported_crops} t={t} />
        <p className="limitation-note">{result.limitations}</p>
      </div>
    );
  }

  const confidence = Number(result.confidence);

  return (
    <div className="result-content">
      <div className="result-title">
        <div className="result-symbol">
          <Icon name="check" size={24} />
        </div>
        <div>
          <p className="eyebrow">{t("fertilizerResult")}</p>
          <h3>{result.fertilizer || "—"}</h3>
        </div>
        {Number.isFinite(confidence) && (
          <span className="confidence">
            {confidence.toFixed(1)}% {t("confidence")}
          </span>
        )}
      </div>

      <div className="result-metrics">
        <div>
          <span>{t("selectedCrop")}</span>
          <strong>{result.selected_crop || result.crop || "—"}</strong>
        </div>
        <div>
          <span>{t("cropCategory")}</span>
          <strong>{result.crop_category || "—"}</strong>
        </div>
      </div>

      <WarningList warnings={result.warnings} t={t} />

      {result.guidance && (
        <div className="prescription">
          <strong>
            <Icon name="sparkle" size={17} />
            {t("guidance")}
          </strong>
          <p>{result.guidance}</p>
        </div>
      )}

      <p className="limitation-note">{t("noDosage")}</p>

      {result.limitations && (
        <div className="limitation-block">
          <h4>{t("limitations")}</h4>
          <p>{result.limitations}</p>
        </div>
      )}

      {result.data_quality?.note && (
        <p className="form-footnote">
          <strong>{t("dataQuality")}:</strong> {result.data_quality.note}
        </p>
      )}
    </div>
  );
}

export default function App() {
  const [language, setLanguage] = useState("en");
  const t = useCallback(
    (key) => TEXT[language]?.[key] || TEXT.en[key] || key,
    [language]
  );

  const [page, setPage] = useState("overview");
  const [farm, setFarm] = useState(INITIAL_FARM);
  const [cropResult, setCropResult] = useState(null);
  const [cropError, setCropError] = useState("");
  const [cropLoading, setCropLoading] = useState(false);
  const [fertilizerResult, setFertilizerResult] = useState(null);
  const [fertilizerError, setFertilizerError] = useState("");
  const [fertilizerLoading, setFertilizerLoading] = useState(false);
  const [selectedFertilizerCrop, setSelectedFertilizerCrop] = useState("");
  const [cropCarried, setCropCarried] = useState("");
  const [trend, setTrend] = useState([]);
  const [trendLoading, setTrendLoading] = useState(false);
  const [trendError, setTrendError] = useState("");
  const [toast, setToast] = useState("");
  const [mobileMenu, setMobileMenu] = useState(false);
  const [message, setMessage] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState("");
  const [chat, setChat] = useState([
    { role: "assistant", text: TEXT.en.welcome },
  ]);

  const menu = [
    { id: "overview", label: t("overview"), icon: "grid" },
    { id: "crop", label: t("cropRecommendation"), icon: "sprout" },
    { id: "fertilizer", label: t("fertilizer"), icon: "flask" },
    { id: "yield", label: t("yield"), icon: "chart" },
    { id: "assistant", label: t("assistant"), icon: "chat" },
  ];

  const navigate = (nextPage) => {
    if (page === "fertilizer" && nextPage !== "fertilizer") {
      setCropCarried("");
    }
    setPage(nextPage);
    setMobileMenu(false);
  };

  async function getCropRecommendation(event) {
    event?.preventDefault();
    setCropLoading(true);
    setCropError("");
    setToast("");

    const payload = {
      N: Number(farm.N),
      P: Number(farm.P),
      K: Number(farm.K),
      temperature: Number(farm.temperature),
      humidity: Number(farm.humidity),
      ph: Number(farm.ph),
      rainfall: Number(farm.rainfall),
      language,
    };

    try {
      const data = await apiRequest("/crop/", {
        method: "POST",
        body: JSON.stringify(payload),
      });

      setCropResult(data);
      setCropError("");
      setToast("Crop recommendation received.");
      const recommendedCrop =
        data.crop_key || data.suitability?.[0]?.crop_key;
      if (recommendedCrop) {
        setSelectedFertilizerCrop(recommendedCrop);
        setFertilizerResult(null);
        setFertilizerError("");
      }
    } catch (error) {
      const message = error.message || t("backendError");
      setCropError(message);
      setToast(message);
    } finally {
      setCropLoading(false);
    }
  }

  async function getFertilizerRecommendation(event) {
    event?.preventDefault();
    setFertilizerLoading(true);
    setFertilizerError("");
    setToast("");

    const payload = {
      crop: farm.fertilizer_crop,
      N: Number(farm.N),
      P: Number(farm.P),
      K: Number(farm.K),
      temperature: Number(farm.temperature),
      humidity: Number(farm.humidity),
      moisture: Number(farm.moisture),
      soil_type: farm.soil_type,
      language,
    };

    try {
      const data = await apiRequest("/fertilizer/", {
        method: "POST",
        body: JSON.stringify(payload),
      });

      setFertilizerResult(data);
      setFertilizerError("");
      setToast(
        data.supported === false
          ? "This crop is not supported by the fertilizer model."
          : "Fertilizer guidance received."
      );
    } catch (error) {
      const message = error.message || t("backendError");
      setFertilizerError(message);
      setToast(message);
    } finally {
      setFertilizerLoading(false);
    }
  }

  async function runFertilizerForCrop(cropKey) {
    if (!cropKey) return;
    setFertilizerLoading(true);
    setFertilizerError("");
    setFertilizerResult(null);
    setToast("");

    const payload = {
      crop: cropKey,
      N: Number(farm.N),
      P: Number(farm.P),
      K: Number(farm.K),
      temperature: Number(farm.temperature),
      humidity: Number(farm.humidity),
      moisture: Number(farm.moisture),
      soil_type: farm.soil_type,
      language,
    };

    try {
      const data = await apiRequest("/fertilizer/", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setFertilizerResult(data);
      setFertilizerError("");
    } catch (error) {
      const message = error.message || t("backendError");
      setFertilizerError(message);
      setToast(message);
    } finally {
      setFertilizerLoading(false);
    }
  }

useEffect(() => {
    if (page === "crop" && cropResult && selectedFertilizerCrop) {
      runFertilizerForCrop(selectedFertilizerCrop);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedFertilizerCrop, page, cropResult]);

  const getTrend = useCallback(async () => {
    setTrendLoading(true);
    setTrendError("");

    try {
      const query = new URLSearchParams({
        crop: farm.trend_crop,
        area: farm.area,
        years: "1993-2013",
      });

      const data = await apiRequest(`/yield_trend/?${query.toString()}`);

      if (!data.success || !Array.isArray(data.records)) {
        setTrend([]);
        setTrendError(data.message || data.error || t("noCropHistory"));
        return;
      }

      const records = data.records
        .map((record) => ({
          year: Number(record.year),
          yield: Number(record.yield),
        }))
        .filter(
          (record) =>
            Number.isFinite(record.year) &&
            Number.isFinite(record.yield) &&
            record.yield >= 0
        )
        .sort((a, b) => a.year - b.year);

      setTrend(records);

      if (records.length === 0) {
        setTrendError(t("noHistory"));
      }
    } catch (error) {
      setTrend([]);
      setTrendError(error.message || t("backendError"));
    } finally {
      setTrendLoading(false);
    }
  }, [farm.trend_crop, farm.area, t]);

  async function sendMessage(event, suggestedText) {
    event?.preventDefault();

    const question = (suggestedText ?? message).trim();
    if (!question || chatLoading) return;

    setChat((previous) => [...previous, { role: "user", text: question }]);
    setMessage("");
    setChatLoading(true);
    setChatError("");

    try {
      const data = await apiRequest("/chat/", {
        method: "POST",
        body: JSON.stringify({
          message: question,
          language,
        }),
      });

      setChat((previous) => [
        ...previous,
        {
          role: "assistant",
          text: data.reply || data.response || "No response was returned.",
        },
      ]);
    } catch (error) {
      setChatError(error.message || t("backendError"));
    } finally {
      setChatLoading(false);
    }
  }

  useEffect(() => {
    if (page !== "yield" && page !== "overview") {
      return undefined;
    }

    const timeout = window.setTimeout(getTrend, 0);
    return () => window.clearTimeout(timeout);
  }, [page, getTrend]);

  useEffect(() => {
    if (!toast) return undefined;
    const timeout = window.setTimeout(() => setToast(""), 5000);
    return () => window.clearTimeout(timeout);
  }, [toast]);

  const pageTitle = menu.find((item) => item.id === page)?.label || t("overview");

  function Sidebar() {
    return (
      <>
        {mobileMenu && (
          <button
            className="mobile-overlay"
            aria-label="Close navigation"
            onClick={() => setMobileMenu(false)}
          />
        )}
        <aside className={`sidebar ${mobileMenu ? "sidebar-open" : ""}`}>
          <div className="brand">
            <div className="brand-mark">
              <Icon name="leaf" size={27} />
            </div>
            <div>
              <strong>Agro<span>Agent</span></strong>
              <small>{t("subtitle")}</small>
            </div>
            <button
              className="mobile-close"
              aria-label="Close menu"
              onClick={() => setMobileMenu(false)}
            >
              <Icon name="close" />
            </button>
          </div>

          <p className="workspace-label">{t("workspace")}</p>
          <nav className="nav-list" aria-label="Main navigation">
            {menu.map((item) => (
              <button
                key={item.id}
                className={`nav-item ${page === item.id ? "active" : ""}`}
                onClick={() => navigate(item.id)}
              >
                <span className="nav-icon">
                  <Icon name={item.icon} size={21} />
                </span>
                <span>{item.label}</span>
                {page === item.id && <i />}
              </button>
            ))}
          </nav>

          <div className="sidebar-spacer" />

          <div className="sidebar-tip">
            <div className="tip-symbol">
              <Icon name="sprout" size={23} />
            </div>
            <strong>{t("fieldTip")}</strong>
            <p>{t("heroDescription")}</p>
            <button onClick={() => navigate("crop")}>
              {t("explore")} <Icon name="arrow" size={14} />
            </button>
          </div>

          <div className="profile-row">
            <div className="profile-avatar">
              <Icon name="leaf" size={18} />
            </div>
            <div>
              <strong>{t("profile")}</strong>
              <small>{t("subtitle")}</small>
            </div>
            <span className="profile-status" />
          </div>
        </aside>
      </>
    );
  }

  function Hero() {
    return (
      <section className="hero">
        <div className="hero-copy">
          <span className="hero-tag">
            <span className="live-dot" />
            {t("subtitle")}
          </span>
          <h1>
            {t("greeting")}
            <br />
            <em>{t("greeting2")}</em>
          </h1>
          <p>{t("heroDescription")}</p>
          <button
            className="button hero-button"
            onClick={() => navigate("crop")}
          >
            <Icon name="sprout" size={19} />
            {t("getStarted")}
            <Icon name="arrow" size={18} />
          </button>
        </div>
        <figure className="hero-image-figure">
          <img
            className="hero-image"
            src={dashboardImage}
            alt="AgroAgent dashboard overview"
            loading="lazy"
          />
        </figure>
      </section>
    );
  }

  function HistoricalCard() {
    return (
      <section className="surface">
        <SectionTitle
          eyebrow="DATA-DRIVEN INSIGHTS"
          title={t("history")}
          description={t("historyNote")}
          action={
            <button
              className="icon-button"
              aria-label={t("refresh")}
              title={t("refresh")}
              onClick={getTrend}
              disabled={trendLoading}
            >
              <Icon name="activity" size={18} />
            </button>
          }
        />

        <div className="yield-filters">
          <div>
            <small>{t("crop")}</small>
            <strong>
              {CROP_LABELS[farm.trend_crop] || farm.trend_crop}
            </strong>
          </div>
          <div>
            <small>{t("area")}</small>
            <strong>{farm.area}</strong>
          </div>
          <div>
            <small>{t("yearRange")}</small>
            <strong>1993–2013</strong>
          </div>
        </div>

        {trendLoading && (
          <div className="history-status">
            <div className="loading-line" />
            <p>{t("loadingHistory")}</p>
          </div>
        )}

        {!trendLoading && trendError && (
          <div className="history-status history-error">
            <Icon name="alert" size={22} />
            <p>{trendError}</p>
            <button className="text-button" onClick={getTrend}>
              {t("refresh")}
            </button>
          </div>
        )}

        {!trendLoading && !trendError && trend.length > 0 && (
          <TrendChart records={trend} t={t} />
        )}
      </section>
    );
  }

  function OverviewPage() {
    const latestTrend = trend.length > 0 ? trend[trend.length - 1] : null;

    return (
      <>
        <Hero />

        <figure className="farm-banner-figure">
          <img
            className="farm-banner dashboard-image"
            src={dashboardImage}
            alt="AgroAgent dashboard overview"
            loading="lazy"
          />
          <figcaption>Field-ready insights for crop and fertilizer planning</figcaption>
        </figure>

        <div className="metric-grid">
          <Metric
            icon="sprout"
            label={t("cropMetric")}
            value={cropResult?.crop || t("waiting")}
            note={cropResult ? t("latestResult") : t("waiting")}
            color="green"
          />
          <Metric
            icon="flask"
            label={t("fertilizerMetric")}
            value={
              fertilizerResult?.supported === false
                ? "—"
                : fertilizerResult?.fertilizer || "—"
            }
            note={
              fertilizerResult ? t("latestResult") : t("waiting")
            }
            color="gold"
          />
          <Metric
            icon="chart"
            label={t("yieldMetric")}
            value={
              latestTrend
                ? Number(latestTrend.yield).toFixed(2)
                : "—"
            }
            note={
              latestTrend
                ? `${latestTrend.year} · ${t("historicalYieldNote")}`
                : t("waiting")
            }
            color="blue"
          />
          <Metric
            icon="water"
            label={t("soilMetric")}
            value={farm.ph}
            note={`${farm.soil_type} · ${farm.moisture}% moisture`}
            color="teal"
          />
        </div>

        <div className="dashboard-grid">
          <HistoricalCard />

          <section className="surface quick-card">
            <SectionTitle
              eyebrow="YOUR WORKSPACE"
              title={t("quickActions")}
              description={t("quickDescription")}
            />

            {[
              ["sprout", t("openCrop"), t("cropDescription"), "crop"],
              ["flask", t("openFertilizer"), t("fertilizerDescription"), "fertilizer"],
              ["chart", t("openYield"), t("yieldDescription"), "yield"],
              ["chat", t("assistantAction"), t("assistantDescription"), "assistant"],
            ].map(([icon, title, description, destination], index) => (
              <button
                className="quick-action"
                key={destination}
                onClick={() => navigate(destination)}
              >
                <span className={`quick-icon ${index === 2 ? "gold" : ""}`}>
                  <Icon name={icon} size={21} />
                </span>
                <span className="quick-copy">
                  <strong>{title}</strong>
                  <small>{description}</small>
                </span>
                <Icon name="arrow" size={18} />
              </button>
            ))}
          </section>
        </div>

        <div className="bottom-grid">
          <section className="surface">
            <SectionTitle
              eyebrow="FIELD CONDITIONS"
              title={t("currentConditions")}
              description={t("conditionsDescription")}
            />
            <div className="conditions">
              {[
                ["sun", t("temperature"), `${farm.temperature} °C`],
                ["water", t("humidity"), `${farm.humidity}%`],
                ["water", t("rainfall"), `${farm.rainfall} mm`],
                ["leaf", t("soilType"), farm.soil_type],
              ].map(([icon, label, value]) => (
                <div className="condition" key={label}>
                  <Icon name={icon} size={21} />
                  <span>{label}</span>
                  <strong>{value}</strong>
                </div>
              ))}
            </div>
            <button
              className="text-button"
              onClick={() => navigate("crop")}
            >
              {t("farmInputs")} <Icon name="arrow" size={15} />
            </button>
          </section>

          <section className="surface insight-card">
            <div className="insight-icon">
              <Icon name="sparkle" size={24} />
            </div>
            <p className="eyebrow">AGROAGENT INSIGHT</p>
            <h3>{t("prescription")}</h3>
            <p>
              {cropResult?.explanation ||
                "Enter your farm measurements to receive a model-based crop recommendation. Use the AI assistant for additional farming questions."}
            </p>
            <button
              className="button button-primary"
              onClick={() => navigate("assistant")}
            >
              <Icon name="chat" size={18} />
              {t("assistantAction")}
            </button>
          </section>
        </div>
      </>
    );
  }

  function CropPage() {
    const recommendedCrops =
      Array.isArray(cropResult?.suitability) && cropResult.suitability.length > 0
        ? cropResult.suitability.slice(0, 6)
        : cropResult?.crop_key
        ? [
            {
              crop_key: cropResult.crop_key,
              crop: cropResult.crop,
              prob: cropResult.confidence / 100,
            },
          ]
        : [];

    return (
      <>
        <SectionTitle
          eyebrow="CROP ADVISOR"
          title={t("cropHeading")}
          description={t("cropDescription")}
        />

        <figure className="page-banner">
          <img
            src={cropImage}
            alt="Crop recommendation"
            loading="lazy"
          />
        </figure>

        <div className="form-layout">
          <section className="surface form-card">
            <CropForm
              farm={farm}
              setFarm={setFarm}
              onSubmit={getCropRecommendation}
              loading={cropLoading}
              t={t}
            />
          </section>

          <section className="surface result-card">
            <SectionTitle
              eyebrow="MODEL OUTPUT"
              title={t("cropResult")}
              description={t("resultDescription")}
            />
            <CropResultPanel
              result={cropResult}
              loading={cropLoading}
              error={cropError}
              t={t}
            />
          </section>
        </div>

        <section className="surface fertilizer-advisor fade-in">
          <SectionTitle
            eyebrow="CROP-BASED FERTILIZER ADVISOR"
            title="Fertilizer guidance for the selected crop"
            description="Choose a recommended crop below. Fertilizer guidance updates automatically using the current soil and weather inputs."
          />

          {!cropResult ? (
            <ResultMessage
              icon="flask"
              title={t("noResult")}
              description="Run a crop recommendation first. Then choose a recommended crop here to see its fertilizer guidance."
              t={t}
            />
          ) : (
            <>
              <div className="fertilizer-selection">
                <label className="field">
                  <span>{t("fertilizerCrop")}</span>
                  <select
                    value={selectedFertilizerCrop}
                    onChange={(event) =>
                      setSelectedFertilizerCrop(event.target.value)
                    }
                    disabled={fertilizerLoading}
                  >
                    {recommendedCrops.map((item) => (
                      <option key={item.crop_key} value={item.crop_key}>
                        {item.crop}
                      </option>
                    ))}
                  </select>
                </label>
                <button
                  type="button"
                  className="button button-secondary"
                  disabled
                  aria-disabled="true"
                >
                  <Icon name="flask" size={17} />
                  {t("getFertilizer")}
                </button>
              </div>

              <FertilizerResultPanel
                result={fertilizerResult}
                loading={fertilizerLoading}
                error={fertilizerError}
                t={t}
              />
            </>
          )}
        </section>

        <div className="notice">
          <Icon name="alert" size={21} />
          <div>
            <strong>{t("useCarefully")}</strong>
            <p>{t("safetyText")}</p>
          </div>
        </div>
      </>
    );
  }

  function FertilizerPage() {
    return (
      <>
        <SectionTitle
          eyebrow="FERTILIZER ADVISOR"
          title={t("fertilizerHeading")}
          description={t("fertilizerDescription")}
        />

        <figure className="page-banner">
          <img
            src={fertilizerImage}
            alt="Fertilizer recommendation"
            loading="lazy"
          />
        </figure>

        <div className="form-layout">
          <section className="surface form-card">
            <FertilizerForm
              farm={farm}
              setFarm={setFarm}
              onSubmit={getFertilizerRecommendation}
              loading={fertilizerLoading}
              t={t}
              cropCarried={cropCarried}
              clearCropCarried={() => setCropCarried("")}
            />
          </section>

          <section className="surface result-card">
            <SectionTitle
              eyebrow="MODEL OUTPUT"
              title={t("fertilizerResult")}
              description={t("resultDescription")}
            />
            <FertilizerResultPanel
              result={fertilizerResult}
              loading={fertilizerLoading}
              error={fertilizerError}
              t={t}
            />
          </section>
        </div>

        <div className="notice">
          <Icon name="alert" size={21} />
          <div>
            <strong>{t("useCarefully")}</strong>
            <p>{t("safetyText")}</p>
          </div>
        </div>
      </>
    );
  }

  function YieldPage() {
    return (
      <>
        <SectionTitle
          eyebrow="DATA EXPLORER"
          title={t("yieldHeading")}
          description={t("yieldDescription")}
        />

        <div className="surface yield-card">
          <div className="yield-filters">
            <label className="field">
              <span>{t("crop")}</span>
              <select
                value={farm.trend_crop}
                onChange={(event) =>
                  setFarm((previous) => ({
                    ...previous,
                    trend_crop: event.target.value,
                  }))
                }
              >
                {YIELD_CROP_OPTIONS.map(([value, label]) => (
                  <option value={value} key={value}>
                    {label}
                  </option>
                ))}
              </select>
            </label>

            <label className="field">
              <span>{t("area")}</span>
              <input
                value={farm.area}
                onChange={(event) =>
                  setFarm((previous) => ({
                    ...previous,
                    area: event.target.value,
                  }))
                }
              />
            </label>

            <button
              className="button button-primary"
              onClick={getTrend}
              disabled={trendLoading}
            >
              <Icon name="chart" size={18} />
              {trendLoading ? t("loadingHistory") : t("refresh")}
            </button>
          </div>

          <HistoricalCard />
        </div>

        <div className="notice">
          <Icon name="activity" size={21} />
          <div>
            <strong>{t("historicalSource")}</strong>
            <p>{t("historyNote")} {t("yearRange")}</p>
          </div>
        </div>
      </>
    );
  }

  function AssistantPage() {
    const prompts = [t("prompt1"), t("prompt2"), t("prompt3")];

    return (
      <>
        <SectionTitle
          eyebrow="AI FARMING SUPPORT"
          title={t("assistantHeading")}
          description={t("assistantDescription")}
        />

        <section className="surface chat-card">
          <div className="chat-heading">
            <div className="assistant-avatar">
              <Icon name="sparkle" size={23} />
            </div>
            <div>
              <strong>AgroAgent AI</strong>
              <small>
                <span className="live-dot" />
                {t("assistantOnline")}
              </small>
            </div>
          </div>

          <div className="chat-messages" aria-live="polite">
            {chat.map((item, index) => (
              <div
                className={`chat-message ${item.role === "user" ? "user" : ""}`}
                key={`${index}-${item.role}`}
              >
                {item.role === "assistant" && (
                  <span className="chat-mini-avatar">
                    <Icon name="leaf" size={17} />
                  </span>
                )}
                <p>{item.text}</p>
              </div>
            ))}

            {chatLoading && (
              <div className="chat-message">
                <span className="chat-mini-avatar">
                  <Icon name="sparkle" size={17} />
                </span>
                <p className="chat-wait">{t("thinking")}</p>
              </div>
            )}
          </div>

          <div className="suggested-prompts">
            <span>{t("suggestions")}</span>
            {prompts.map((prompt) => (
              <button
                key={prompt}
                type="button"
                disabled={chatLoading}
                onClick={() => sendMessage(null, prompt)}
              >
                {prompt}
              </button>
            ))}
          </div>

          <form className="chat-form" onSubmit={sendMessage}>
            <input
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              placeholder={t("typeQuestion")}
              aria-label={t("typeQuestion")}
              disabled={chatLoading}
            />
            <button
              className="button button-primary"
              type="submit"
              disabled={chatLoading || !message.trim()}
            >
              <Icon name="send" size={18} />
              {t("send")}
            </button>
          </form>

          {chatError && (
            <div className="chat-error" role="alert">
              <Icon name="alert" size={17} />
              <span>{chatError}</span>
              <button onClick={() => setChatError("")} aria-label={t("dismiss")}>
                <Icon name="close" size={17} />
              </button>
            </div>
          )}

          <p className="chat-disclaimer">{t("disclaimer")}</p>
        </section>
      </>
    );
  }

function renderCurrentPage() {
  switch (page) {
    case "overview":
      return OverviewPage();

    case "crop":
      return CropPage();

    case "fertilizer":
      return FertilizerPage();

    case "yield":
      return YieldPage();

    case "assistant":
      return AssistantPage();

    default:
      return OverviewPage();
  }
}

  return (
    <div className="app-shell">
      {Sidebar()}

      <main className="main-area">
        <header className="topbar">
          <div className="topbar-left">
            <button
              className="mobile-menu-button"
              aria-label="Open navigation"
              onClick={() => setMobileMenu(true)}
            >
              <Icon name="menu" size={23} />
            </button>
            <div className="breadcrumb">
              {t("dashboard")} <span>/</span> <strong>{pageTitle}</strong>
            </div>
          </div>

          <div className="topbar-right">
            <label className="language-select">
              <Icon name="globe" size={18} />
              <span className="sr-only">{t("language")}</span>
              <select
                aria-label={t("language")}
                value={language}
                onChange={(event) => {
                  const nextLanguage = event.target.value;
                  setLanguage(nextLanguage);
                  setChat((previous) => {
                    if (
                      previous.length === 1 &&
                      previous[0].role === "assistant"
                    ) {
                      return [
                        {
                          role: "assistant",
                          text: TEXT[nextLanguage].welcome,
                        },
                      ];
                    }
                    return previous;
                  });
                }}
              >
                <option value="en">{t("english")}</option>
                <option value="ta">{t("tamil")}</option>
              </select>
            </label>

            <div className="date-pill">
              <Icon name="calendar" size={17} />
              <span>{t("today")}</span>
            </div>

            <div className="top-avatar" title="AgroAgent">
              <Icon name="leaf" size={17} />
            </div>
          </div>
        </header>

        <div className="page-container">
          {renderCurrentPage()}

          <footer className="app-footer">
            <span>{t("footer")}</span>
          </footer>
        </div>
      </main>

      {toast && (
        <div className="toast" role="status">
          <span>{toast}</span>
          <button
            onClick={() => setToast("")}
            aria-label={t("dismiss")}
          >
            <Icon name="close" size={18} />
          </button>
        </div>
      )}
    </div>
  );
}
