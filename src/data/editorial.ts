/** Source-grounded editorial content. Public institution projects are industry references only. */

export interface EditorialSection {
  heading: string;
  paragraphs: string[];
}

export interface CaseReference {
  title: string;
  text: string;
  sourceLabel: string;
  sourceUrl: string;
  note: string;
  image?: string;
  imageAlt?: string;
  imageCaption?: string;
}

export interface Solution {
  slug: string;
  title: string;
  summary: string;
  image: string;
  imageAlt: string;
  imageCaption: string;
  index: string;
  topic: string;
  productIds: string[];
  productNames: string[];
  productImage: string;
  productImageAlt: string;
  sourceNote: string;
  sections: EditorialSection[];
  caseReference: CaseReference;
}

export interface Article {
  kind?: 'product';
  slug: string;
  title: string;
  summary: string;
  image: string;
  imageAlt: string;
  imageCaption: string;
  topic: string;
  caseYear: string;
  publisher: string;
  sourceUrl: string;
  sourceLabel: string;
  paragraphs: string[];
  relatedProducts: { name: string; id: string }[];
  supportImage?: string;
  supportImageAlt?: string;
  supportImageCaption?: string;
}

export const solutions: Solution[] = [
  {
    slug: 'ecological-mapping',
    title: '轻型航测与生态监测',
    summary: '围绕生态样地、施工区域和线状地物，规划影像采集、正射成果与周期对比。',
    image: '/media/editorial/usgs-2023-meadow.webp',
    imageAlt: 'USGS 人员在 Ackerson Meadow 使用无人机开展测绘的行业资料图',
    imageCaption: '行业资料图：USGS 2023 年 Ackerson Meadow 测绘现场，非 YH 产品项目。',
    index: '01',
    topic: '生态与测绘',
    productIds: ['uav-y-200'],
    productNames: ['Y-200'],
    productImage: '/media/editorial/y200-field.webp',
    productImageAlt: 'Y-200 轻型复合翼无人机画册现场图',
    sourceNote: 'Y-200 参数据提供的 UAV_CN&ENG.pdf 第 12 页；任务成果应按相机和后处理配置核定。',
    sections: [
      {
        heading: '从成果反推任务',
        paragraphs: [
          '先明确要获得正射影像、植被变化记录还是现场视频，再确定相机、覆盖范围与重复采集频次。把每次影像和飞行记录按区域与日期归档，才能形成可对照的资料。',
        ],
      },
      {
        heading: '平台选型',
        paragraphs: [
          'Y-200 采用电动垂直起降，画册列有正射相机、多光谱相机和光电吊舱选项。资料标注任务载荷不超过 1.2 kg、续航 2 小时、控制半径 30 km、组装时间不超过 5 分钟。具体配置须同时核对相机重量、供电和安装接口。',
        ],
      },
      {
        heading: '实施与验证',
        paragraphs: [
          '航线和影像处理应围绕目标分辨率与覆盖范围设计。画册没有给出测绘精度，不能以续航或载荷代替最终成果精度；相机、控制点、航线和后处理都需要在项目中验证。',
        ],
      },
    ],
    caseReference: {
      title: 'USGS：生态修复区正射影像',
      text: '2016 年，美国地质调查局在印第安纳州的低地生态修复区采集自然色与多光谱影像，生成可对照的正射成果。它展示了同类数据流程的价值。',
      sourceLabel: '查看 USGS 原始图文',
      sourceUrl:
        'https://www.usgs.gov/media/images/orthomosaic-generated-natural-color-imagery-a-sensor-mounted-a-uas',
      note: '该项目没有使用 Y-200 的证据；顶部图片来自 USGS 2023 年的另一处测绘现场。',
      image: '/media/editorial/usgs-2016-orthomosaic.webp',
      imageAlt: 'USGS 2016 年低地生态修复区的正射影像',
      imageCaption: '图片：USGS，2016 年生态修复区正射影像。',
    },
  },
  {
    slug: 'infrastructure-inspection',
    title: '工业设施与线性资产巡检',
    summary: '为分散站点、管线和大型设施建立可复核的可见光与热像巡检记录。',
    image: '/media/editorial/y500-product.webp',
    imageAlt: 'Y-500 油动复合翼无人机画册产品图',
    imageCaption: '图片：提供的 UAV 产品画册。',
    index: '02',
    topic: '设施巡检',
    productIds: ['uav-y-500'],
    productNames: ['Y-500'],
    productImage: '/media/editorial/y500-product.webp',
    productImageAlt: 'Y-500 油动复合翼无人机产品图',
    sourceNote:
      'Y-500 参数据提供的 UAV_CN&ENG.pdf 第 11 页；各项最大值不代表同一任务下可同时达到。',
    sections: [
      {
        heading: '覆盖与记录',
        paragraphs: [
          '跨区域设施巡检需要把照片、热像与资产编号对应起来。先按线路长度和站点分布划分任务区段，再统一异常类别与拍摄视角，便于人工复核。',
        ],
      },
      {
        heading: '平台选型',
        paragraphs: [
          'Y-500 采用电动垂直起降、燃油巡航。画册分别列出最大续航 4 小时、任务载荷 40 kg 和 20–50 km 数据与视频链路，并介绍可见光、热成像与 30 倍光学变焦选项。',
        ],
      },
      {
        heading: '实施与验证',
        paragraphs: [
          '相机组合、接口与实际带载航时应在配置阶段确认。尤其不要把最大续航、最大载荷和最远链路理解为可同时实现的单一作业状态。',
        ],
      },
    ],
    caseReference: {
      title: '美国能源部：Savannah River Site 设施检查',
      text: '美国能源部 2026 年报道，该场址使用无人机检查储水罐、管道走廊、屋顶等设施，并由人员复核影像。这说明影像必须进入明确的维护流程。',
      sourceLabel: '查看美国能源部原文',
      sourceUrl:
        'https://www.energy.gov/em/articles/savannah-river-site-partnership-strengthens-drone-inspection-capabilities',
      note: '报道没有表明该场址使用 Y-500。本站所示为相关产品画册图，并非案例现场。',
    },
  },
  {
    slug: 'near-field-survey',
    title: '园区近距巡查与定点观察',
    summary: '面向厂区、园区和施工现场，以灵活起降与定点悬停完成近距观察。',
    image: '/media/editorial/y40-scene.webp',
    imageAlt: 'Y-40 四旋翼无人机画册场景图',
    imageCaption: '图片：提供的 UAV 产品画册；原图分辨率较低，仅作场景示意。',
    index: '03',
    topic: '园区巡查',
    productIds: ['uav-y-40'],
    productNames: ['Y-40'],
    productImage: '/media/editorial/y40-scene.webp',
    productImageAlt: 'Y-40 四旋翼无人机画册场景图',
    sourceNote: 'Y-40 参数据提供的 UAV_CN&ENG.pdf 第 13 页；画册未指定标准相机。',
    sections: [
      {
        heading: '固定点位复拍',
        paragraphs: [
          '屋顶、立面和管道接口需要多角度观察。可把常规巡查路线与重点点位复拍结合，将照片和工单编号关联，使变化更容易被复核。',
        ],
      },
      {
        heading: '平台选型',
        paragraphs: [
          'Y-40 为电动四旋翼平台。画册标注 1 kg 载荷条件下续航 70 分钟，安全负重不超过 5 kg，并列有 RTK 差分导航及 15–20 km 数据与视频链路。',
        ],
      },
      {
        heading: '实施与验证',
        paragraphs: [
          '镜头、拍摄距离和兼容载荷应按目标部位确认。画册未指定标准相机，不应将热像、测温或某种分辨率写为标配。',
        ],
      },
    ],
    caseReference: {
      title: '美国能源部：Hanford 屋顶检查',
      text: '美国能源部 2026 年介绍 Hanford 场址通过无人机查看停用设施的屋面、通风口和可能的漏水路径，减少人员在高处检查的需要。',
      sourceLabel: '查看美国能源部原文',
      sourceUrl:
        'https://www.energy.gov/em/articles/hanford-builds-drone-program-improve-facility-inspections',
      note: '报道未提及 Y-40；画册图片不是 Hanford 项目现场。',
    },
  },
  {
    slug: 'emergency-observation',
    title: '应急态势观察与通信任务平台',
    summary: '先建立灾后区域的空中态势观察，再按任务评估通信载荷集成。',
    image: '/media/editorial/usgs-2018-fire.webp',
    imageAlt: 'USGS 人员在 Whiskeytown 火灾区域开展无人机调查的行业资料图',
    imageCaption: '行业资料图：USGS 2018 年火灾区域调查，非 YH 产品或 Verizon 通信案例。',
    index: '04',
    topic: '应急观察',
    productIds: ['yh-yh-2000'],
    productNames: ['YH-2000'],
    productImage: '/media/editorial/yh2000-view.webp',
    productImageAlt: 'YH-2000 垂直起降固定翼无人机画册视图',
    sourceNote: 'YH-2000 参数据提供的 PRODUCT CATALOGUE V6.pdf 第 4 页；通信载荷须单独设计验证。',
    sections: [
      {
        heading: '先看清现场',
        paragraphs: [
          '应急现场需要快速识别道路、积水、设施与通道状态。空中观察平台可按区域和时间整理影像，支持现场判断与事后复盘。',
        ],
      },
      {
        heading: '平台选型',
        paragraphs: [
          'YH-2000 为垂直起降固定翼平台。画册把应急通信列为应用方向，并分别列出最大载荷 15 kg、最大续航 600 分钟、航程 850 km 和可定制控制半径 50–100 km。',
        ],
      },
      {
        heading: '通信任务需另行集成',
        paragraphs: [
          '画册没有列出具体通信中继模块。若承担此类任务，应另行核对设备重量、供电、天线、回传和持续运行方式；不能把应用方向等同于已具备空中基站能力。',
        ],
      },
    ],
    caseReference: {
      title: 'Verizon：飓风 Ian 后的临时空中通信',
      text: 'Verizon 记录了在佛罗里达州灾后使用系留无人机搭载蜂窝设备，为部分受影响区域提供临时覆盖。这个案例展示了飞行平台、供电和网络回传协同的需求。',
      sourceLabel: '查看 Verizon 官方记录',
      sourceUrl: 'https://www.verizon.com/about/news/verizon-responds-hurricane-ian',
      note: 'Verizon 使用的是系留系统，不是 YH-2000；不能据此推断 YH-2000 已具备蜂窝基站能力。',
    },
  },
  {
    slug: 'wide-area-survey',
    title: '大范围巡查与周期性区域观察',
    summary: '围绕覆盖区、载荷和复飞可比性，规划较大区域的周期性影像采集。',
    image: '/media/editorial/mdg48-scene.webp',
    imageAlt: 'MD-G48 垂起复合翼无人机画册场景图',
    imageCaption: '图片：提供的产品画册。',
    index: '05',
    topic: '区域观察',
    productIds: ['md-md-g44', 'md-md-g48'],
    productNames: ['MD-G44', 'MD-G48'],
    productImage: '/media/editorial/mdg48-scene.webp',
    productImageAlt: 'MD-G48 垂起复合翼无人机画册场景图',
    sourceNote: 'MD-G44、MD-G48 参数据提供的产品画册第 11–12 页；所列航时均为空载指标。',
    sections: [
      {
        heading: '定义可比的周期任务',
        paragraphs: [
          '大范围观察应先确定覆盖区、目标分辨率、传感器质量和每次复飞的条件，再将影像与时间、区域、任务设备关联。',
        ],
      },
      {
        heading: '平台选型',
        paragraphs: [
          '画册列出 MD-G44 最大载荷 10 kg、空载航时 480 分钟；MD-G48 最大载荷 15 kg、空载航时 780 分钟。两款产品可进入不同载荷需求的初筛清单。',
        ],
      },
      {
        heading: '带载验证',
        paragraphs: [
          '传感器接口、供电和实际带载航时需要另行核对。空载航时不能直接用于推算挂载后的任务时间，也不能据此承诺特定 LiDAR 集成。',
        ],
      },
    ],
    caseReference: {
      title: 'USGS：火烧迹地区域数据采集',
      text: '2021 年，USGS 在科罗拉多州 East Troublesome Fire 火烧区域采集无人机 LiDAR 数据，用于火后地形与环境研究。案例体现区域数据采集与后续比较的工作链。',
      sourceLabel: '查看 USGS 原始资料',
      sourceUrl:
        'https://www.usgs.gov/media/images/uas-collecting-lidar-over-east-troublesome-fire-burn-scar',
      note: '案例设备不是 MD-G44 或 MD-G48，画册也未列明这两款型号的 LiDAR 接口。',
      image: '/media/editorial/usgs-2021-burn.webp',
      imageAlt: 'USGS 在 East Troublesome Fire 火烧迹地采集无人机 LiDAR 数据的现场图',
      imageCaption: '图片：USGS，2021 年火烧迹地测绘现场；图中非 YH 产品。',
    },
  },
  {
    slug: 'carbon-fiber-integration',
    title: '碳纤维机架与行业无人机集成',
    summary: '从轴距、壳体重量和安装空间出发，完成机架选择与整机验证。',
    image: '/media/editorial/workshop.webp',
    imageAlt: '提供的产品画册中的复合材料车间场景',
    imageCaption: '图片：提供的产品画册，作为复合材料制造场景。',
    index: '06',
    topic: '结构与集成',
    productIds: ['md-md-x8', 'md-hw61600', 'md-hi4830'],
    productNames: ['MD-X8', 'HW61600', 'HI4830'],
    productImage: '/media/editorial/mdx8-view.webp',
    productImageAlt: 'MD-X8 碳纤维机架产品视图',
    sourceNote: '三款机架资料据提供的产品画册第 14、15、18 页；尺寸和重量不能跨型号拼接。',
    sections: [
      {
        heading: '从结构要求开始',
        paragraphs: [
          '机架选型需要核对轴距、壳体重量、任务载荷、安装空间与维护方式。目标不是仅选择外形，而是为动力、供电、控制器和任务设备找到合适布局。',
        ],
      },
      {
        heading: '画册型号',
        paragraphs: [
          'MD-X8 对称轴距 2400 mm、壳体重量 15.5 kg；HW61600 对称轴距 1600 mm、壳体重量 2200 g；HI4830 对称轴距 830 mm、壳体重量 1900 g。每项数据只对应各自型号。',
        ],
      },
      {
        heading: '整机验证',
        paragraphs: [
          '装配后还需检查重心、振动、散热、检修空间与飞行表现。壳体重量不等于整机重量，最终能力以目标配置和实际测试为准。',
        ],
      },
    ],
    caseReference: {
      title: 'NASA Langley：八旋翼机体风洞研究',
      text: 'NASA 2023 年公开研究在低速风洞中测试一款商用八旋翼机体，测量气动力、力矩和功率等数据，说明机架几何与旋翼工作状态需要共同评估。',
      sourceLabel: '查看 NASA 技术论文',
      sourceUrl:
        'https://ntrs.nasa.gov/api/citations/20230007169/downloads/AltamiranoEtAL_AVIATION2023_FINAL_V04.pdf',
      note: '研究对象不是本站画册中的机架，不能用于验证 MD-X8、HW61600 或 HI4830 的性能。',
      image: '/media/editorial/hw61600-top.webp',
      imageAlt: 'HW61600 碳纤维机架壳体俯视图',
      imageCaption: '图片：提供的产品画册，HW61600 壳体俯视图；非 NASA 测试设备。',
    },
  },
];

export const articles: Article[] = [
  {
    slug: 'repeatable-aerial-imagery',
    title: '生态修复为什么需要可重复的空中影像',
    summary: '从一次飞行照片到可对照的正射图，生态项目更需要可重复的数据流程。',
    image: '/media/editorial/usgs-2016-orthomosaic.webp',
    imageAlt: 'USGS 2016 年低地生态修复区的无人机正射影像',
    imageCaption: '图片：USGS，2016 年印第安纳州生态修复区正射影像。',
    topic: '行业观察',
    caseYear: '2016',
    publisher: '美国地质调查局 USGS',
    sourceUrl:
      'https://www.usgs.gov/media/images/orthomosaic-generated-natural-color-imagery-a-sensor-mounted-a-uas',
    sourceLabel: 'USGS 原始图文',
    paragraphs: [
      'USGS 在印第安纳州的低地生态修复区采集自然色与多光谱影像，并制作正射影像。正射图把零散照片组织为空间成果，便于记录地表状态，也为后续比对提供基础。',
      '这类任务首先要定义需要观察的变化，再选择影像类型、采集频次和处理方式。相机、控制点、航线和成果归档，决定数据能否被长期使用。',
      'Y-200 画册列有正射相机和多光谱相机选项，可进入同类任务的平台评估；没有证据表明 USGS 项目使用了该型号。',
    ],
    relatedProducts: [{ name: 'Y-200', id: 'uav-y-200' }],
    supportImage: '/media/editorial/usgs-2023-meadow.webp',
    supportImageAlt: 'USGS 2023 年在 Ackerson Meadow 开展无人机测绘的现场图',
    supportImageCaption:
      '图片：USGS 2023 年 Ackerson Meadow，属于另一项工作，不是 2016 年项目现场。',
  },
  {
    slug: 'facility-inspection-workflow',
    title: '无人机巡检如何进入设施维护流程',
    summary: '让飞行影像对应具体设施和检查记录，才能支持后续维护。',
    image: '/media/editorial/y500-product.webp',
    imageAlt: 'Y-500 油动复合翼无人机画册产品图',
    imageCaption: '图片：提供的产品画册，相关平台示意；非 Savannah River Site 项目现场。',
    topic: '行业观察',
    caseYear: '2026',
    publisher: '美国能源部',
    sourceUrl:
      'https://www.energy.gov/em/articles/savannah-river-site-partnership-strengthens-drone-inspection-capabilities',
    sourceLabel: '美国能源部原文',
    paragraphs: [
      '美国能源部介绍 Savannah River Site 使用无人机检查储水罐、管道走廊、屋顶和供配电设施。当地团队把影像与具体设施和维护责任对应起来。',
      '对工业巡检而言，先定义资产清单、异常类型与复核责任，再设计飞行路线和文件命名，能够让空中视角进入可追踪的维护流程。',
      'Y-500 画册列有可见光与热成像等任务选项，但报道没有表明该场址使用了 Y-500；公开案例中的成果也不能当作该型号的性能承诺。',
    ],
    relatedProducts: [{ name: 'Y-500', id: 'uav-y-500' }],
  },
  {
    slug: 'disaster-communication-system',
    title: '灾后空中通信依赖哪些环节',
    summary: '临时通信覆盖需要平台、供电、通信设备与网络回传共同工作。',
    image: '/media/editorial/yh2000-view.webp',
    imageAlt: 'YH-2000 垂直起降固定翼无人机画册产品视图',
    imageCaption: '图片：提供的产品画册，候选平台示意；非 Verizon 项目设备。',
    topic: '行业观察',
    caseYear: '2022',
    publisher: 'Verizon',
    sourceUrl: 'https://www.verizon.com/about/news/verizon-responds-hurricane-ian',
    sourceLabel: 'Verizon 官方记录',
    paragraphs: [
      '飓风 Ian 之后，Verizon 记录了在佛罗里达州受影响区域使用系留无人机搭载蜂窝设备，提供临时空中覆盖。其系统还依赖供电、地面设备和网络回传。',
      '把应用拆开看，飞行平台负责到达任务位置，通信设备负责覆盖，供电和回传决定服务是否能够持续。这些环节都需要在系统级设计中共同验证。',
      'YH-2000 画册把应急通信列为应用方向，但它不是 Verizon 使用的系留无人机；不能由该案例推断 YH-2000 已具备空中基站能力。',
    ],
    relatedProducts: [{ name: 'YH-2000', id: 'yh-yh-2000' }],
  },
  {
    slug: 'airframe-system-validation',
    title: '从机架材料到整机表现，还缺哪一步',
    summary: '轴距和壳体重量只是起点，动力、旋翼和任务载荷仍需整机验证。',
    image: '/media/editorial/mdx8-view.webp',
    imageAlt: 'MD-X8 碳纤维机架画册产品视图',
    imageCaption: '图片：提供的产品画册，MD-X8 机架；非 NASA 风洞测试对象。',
    topic: '技术观察',
    caseYear: '2023',
    publisher: 'NASA Langley',
    sourceUrl:
      'https://ntrs.nasa.gov/api/citations/20230007169/downloads/AltamiranoEtAL_AVIATION2023_FINAL_V04.pdf',
    sourceLabel: 'NASA 技术论文',
    paragraphs: [
      'NASA Langley 的研究在低速风洞中测试一款商用八旋翼机体，对气动力、力矩与功率进行测量。研究提示机架几何、旋翼状态和系统功耗需要共同评估。',
      '进入项目设计时，除核对轴距与壳体重量，还应检查电机、旋翼、电池、任务设备的布局，以及重心、振动和检修空间。',
      'MD-X8、HW61600 与 HI4830 的画册数据可用于结构初筛。NASA 研究对象并非这些型号，不能据此判断它们的实际载重或续航。',
    ],
    relatedProducts: [
      { name: 'MD-X8', id: 'md-md-x8' },
      { name: 'HW61600', id: 'md-hw61600' },
      { name: 'HI4830', id: 'md-hi4830' },
    ],
    supportImage: '/media/editorial/workshop.webp',
    supportImageAlt: '提供的产品画册中的复合材料车间场景',
    supportImageCaption: '图片：提供的产品画册，制造场景示意；非 NASA 研究现场。',
  },
  {
    kind: 'product',
    slug: 'light-vtol-selection-guide',
    title: '轻型垂起复合翼选型指南',
    summary: '从任务成果、载荷与现场组织方式出发，核对 Y-200 的画册配置。',
    image: '/media/editorial/y200-field.webp',
    imageAlt: 'Y-200 轻型垂起复合翼无人机画册现场图',
    imageCaption: 'Y-200 产品画册现场图。',
    topic: '产品选型',
    caseYear: '',
    publisher: 'YH 产品画册',
    sourceUrl: '/products/uav-y-200/',
    sourceLabel: '查看 Y-200 产品资料',
    paragraphs: [
      '轻型垂起复合翼的选型应先确定任务成果：需要正射影像、多光谱记录，还是现场视频。相机选项决定载荷、供电、接口与后处理流程。',
      'Y-200 画册列有光电吊舱、正射相机和多光谱相机选项，标注任务载荷不超过 1.2 kg、续航 2 小时、控制半径 30 km，采用电动垂直起降。以上是画册指标，具体组合仍需按任务配置核对。',
      '现场还要检查运输、组装、起降空间与航线。画册列出的组装时间不超过 5 分钟，不等同于完整任务准备时间；成果精度也必须由相机、控制点和处理流程验证。',
    ],
    relatedProducts: [{ name: 'Y-200', id: 'uav-y-200' }],
  },
  {
    kind: 'product',
    slug: 'carbon-frame-three-numbers',
    title: '碳纤维机架的三个选型数字',
    summary: '轴距、壳体重量和任务载荷，决定机架初筛的方向。',
    image: '/media/editorial/mdx8-view.webp',
    imageAlt: 'MD-X8 碳纤维机架画册产品视图',
    imageCaption: 'MD-X8 产品画册视图。',
    topic: '结构选型',
    caseYear: '',
    publisher: 'YH 产品画册',
    sourceUrl: '/products/md-md-x8/',
    sourceLabel: '查看 MD-X8 产品资料',
    paragraphs: [
      '第一项是轴距，它影响旋翼布局和整机外形。画册分别列出 MD-X8 对称轴距 2400 mm、HW61600 对称轴距 1600 mm、HI4830 对称轴距 830 mm。',
      '第二项是壳体重量。三款机架的画册值分别为 15.5 kg、2200 g 和 1900 g；壳体重量不是含动力、电池和任务设备的整机重量。',
      '第三项是任务载荷及其对应工况。机架初筛之后，还应核对电机、桨、电池、安装空间、重心与散热，并在目标配置下验证整机表现。不能把不同型号或不同工况的指标拼成一套性能。',
    ],
    relatedProducts: [
      { name: 'MD-X8', id: 'md-md-x8' },
      { name: 'HW61600', id: 'md-hw61600' },
      { name: 'HI4830', id: 'md-hi4830' },
    ],
  },
  {
    kind: 'product',
    slug: 'md-g-payload-guide',
    title: '从载荷需求看 MD-G 系列',
    summary: '用载荷需求划定候选型号，再核对实际带载航时与任务设备接口。',
    image: '/media/editorial/mdg48-scene.webp',
    imageAlt: 'MD-G48 垂起复合翼无人机画册场景图',
    imageCaption: 'MD-G48 产品画册场景图。',
    topic: '产品选型',
    caseYear: '',
    publisher: 'YH 产品画册',
    sourceUrl: '/products/md-md-g48/',
    sourceLabel: '查看 MD-G48 产品资料',
    paragraphs: [
      '选择 MD-G 系列时，先列出任务设备的重量、供电需求和安装方式，再按画册载荷指标进行初筛。MD-G44 最大载荷为 10 kg，MD-G48 最大载荷为 15 kg。',
      '画册同时列出 MD-G44 空载航时 480 分钟、MD-G48 空载航时 780 分钟。这些是空载指标，不能直接作为挂载相机或其他任务设备后的可用作业时间。',
      '进入配置阶段，还需验证重心、接口、供电、带载航时和任务环境。型号之间的指标只用于分别比较，最终选型以目标配置测试为准。',
    ],
    relatedProducts: [
      { name: 'MD-G44', id: 'md-md-g44' },
      { name: 'MD-G48', id: 'md-md-g48' },
    ],
  },
];
