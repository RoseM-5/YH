import source from './mission-content.json';

// These are generated, unbranded scenario illustrations. They do not document real projects or products.
const scenes: Record<string, { image: string; imageAlt: string }> = {
  'boundary-river-inspection': {
    image: '/media/scenes/river-boundary.webp',
    imageAlt: '场景示意：森林中的蜿蜒河道与边界地形',
  },
  'corridor-site-inspection': {
    image: '/media/scenes/power-corridor.webp',
    imageAlt: '场景示意：穿越林地的输电通道与巡检道路',
  },
  'mountain-search-recheck': {
    image: '/media/scenes/mountain-search.webp',
    imageAlt: '场景示意：山区林地中的搜索路线与地面人员',
  },
  'post-disaster-access': {
    image: '/media/scenes/landslide-road.webp',
    imageAlt: '场景示意：滑坡后受阻的山路与桥梁',
  },
  'rescue-site-observation': {
    image: '/media/scenes/rescue-observation.webp',
    imageAlt: '场景示意：洪水后道路、建筑与救援点位的整体观察',
  },
  'yh-2000-inspection-selection': {
    image: '/media/scenes/payload-preflight.webp',
    imageAlt: '场景示意：现场人员核对航空相机载荷与供电设备',
  },
  'cross-region-inspection-records': {
    image: '/media/scenes/inspection-records.webp',
    imageAlt: '场景示意：河道巡检前核对点位与影像记录',
  },
  'mountain-search-task-split': {
    image: '/media/scenes/mountain-search.webp',
    imageAlt: '场景示意：山区林地的广域搜索与地面路线',
  },
  'yh-3000-loaded-endurance': {
    image: '/media/scenes/multirotor-preflight.webp',
    imageAlt: '场景示意：现场人员核对多旋翼载荷与电池',
  },
  'post-disaster-verification': {
    image: '/media/scenes/rescue-observation.webp',
    imageAlt: '场景示意：洪水后道路和建筑的现场复核',
  },
  'construction-stage-inspection': {
    image: '/media/scenes/power-corridor.webp',
    imageAlt: '场景示意：山地通道与设施的广域观察',
  },
  'mountain-station-inspection': {
    image: '/media/scenes/mountain-search.webp',
    imageAlt: '场景示意：山区林地及道路的广域观察',
  },
  'flood-response-updates': {
    image: '/media/scenes/rescue-observation.webp',
    imageAlt: '场景示意：洪水后道路、建筑与救援点位的观察',
  },
  'wildfire-access-recon': {
    image: '/media/scenes/river-boundary.webp',
    imageAlt: '场景示意：森林、河道与外围地形的广域观察',
  },
  'post-earthquake-settlement-recon': {
    image: '/media/scenes/landslide-road.webp',
    imageAlt: '场景示意：山路、桥梁与受阻路段的观察',
  },
  'yh-2000-repeat-inspection-baseline': {
    image: '/media/scenes/inspection-records.webp',
    imageAlt: '场景示意：巡检前核对点位与影像记录',
  },
  'mountain-station-link-and-endurance': {
    image: '/media/scenes/power-corridor.webp',
    imageAlt: '场景示意：穿越林地的通道与山区设施',
  },
  'flood-imagery-update-time': {
    image: '/media/scenes/rescue-observation.webp',
    imageAlt: '场景示意：洪水后道路和建筑的区域观察',
  },
  'yh-3000-multi-point-sorties': {
    image: '/media/scenes/multirotor-preflight.webp',
    imageAlt: '场景示意：现场人员核对多旋翼载荷与电池',
  },
  'two-platform-handoff': {
    image: '/media/scenes/payload-preflight.webp',
    imageAlt: '场景示意：现场人员核对航空相机与任务设备',
  },
};

function withScene<T extends { slug: string }>(entry: T) {
  const scene = scenes[entry.slug];
  if (!scene) throw new Error(`Missing mission scene for ${entry.slug}`);
  return {
    ...entry,
    ...scene,
    imageLabel: '场景示意',
    imageCaption: 'AI 生成场景示意，非实际项目影像。',
  };
}

export const missionContent = {
  ...source,
  solutions: source.solutions.map(withScene),
  articles: source.articles.map(withScene),
};
