console.info("[Outreach UI] egress-optimized-v1 loaded");

console.info("[Outreach UI] acceptance-insights-weekly-1 loaded");

console.info("[Outreach UI] connect-job-delete-multiselect-2 loaded");

const config = window.APP_CONFIG || {};

const els = {
  sidebarCollapseButton:
    document.querySelector("#sidebarCollapseButton"),

  sidebarNavSearch: document.querySelector("#sidebarNavSearch"),
  refreshButton: document.querySelector("#refreshButton"),
  logoutButton: document.querySelector("#logoutButton"),
  workerActivityButton: document.querySelector("#workerActivityButton"),
  workerActivityPopover: document.querySelector("#workerActivityPopover"),
  workerActivityClose: document.querySelector("#workerActivityClose"),
  workerActivitySummary: document.querySelector("#workerActivitySummary"),
  workerActivityList: document.querySelector("#workerActivityList"),
  workerActivityNote: document.querySelector("#workerActivityNote"),
  killProcessButton: document.querySelector("#killProcessButton"),
  stopScanButton: document.querySelector("#stopScanButton"),
  stopScanButtonText: document.querySelector("#stopScanButtonText"),
  systemBadge: document.querySelector("#systemBadge"),
  systemBadgeText: document.querySelector("#systemBadgeText"),
  globalError: document.querySelector("#globalError"),

  sessionStatusButton: document.querySelector("#sessionStatusButton"),
  sessionStatusBadge: document.querySelector("#sessionStatusBadge"),
  sessionStatusModal: document.querySelector("#sessionStatusModal"),
  sessionStatusCloseButton: document.querySelector("#sessionStatusCloseButton"),
  sessionStatusCheckButton: document.querySelector("#sessionStatusCheckButton"),
  sessionStatusSummary: document.querySelector("#sessionStatusSummary"),
  sessionStatusList: document.querySelector("#sessionStatusList"),
  sessionStatusError: document.querySelector("#sessionStatusError"),

  settingsButton: document.querySelector("#settingsButton"),
  settingsModal: document.querySelector("#settingsModal"),
  settingsCloseButton: document.querySelector("#settingsCloseButton"),
  settingsDoneButton: document.querySelector("#settingsDoneButton"),
  settingsRememberTab: document.querySelector("#settingsRememberTab"),
  settingsReduceMotion: document.querySelector("#settingsReduceMotion"),

  totalProfiles: document.querySelector("#totalProfiles"),
  pendingCount: document.querySelector("#pendingCount"),
  processingCount: document.querySelector("#processingCount"),
  completedCount: document.querySelector("#completedCount"),
  failedCount: document.querySelector("#failedCount"),

  profilesTabCount: document.querySelector("#profilesTabCount"),
  queueTabCount: document.querySelector("#queueTabCount"),

  activeProcessBadge: document.querySelector("#activeProcessBadge"),
  activeProcessContent: document.querySelector("#activeProcessContent"),
  readyAccountSummary: document.querySelector("#readyAccountSummary"),
  overviewAccountList: document.querySelector("#overviewAccountList"),
  activityTimeline: document.querySelector("#activityTimeline"),
  lastUpdated: document.querySelector("#lastUpdated"),

  resultSummary: document.querySelector("#resultSummary"),
  searchInput: document.querySelector("#searchInput"),
  sortSelect: document.querySelector("#sortSelect"),
  errorState: document.querySelector("#errorState"),
  emptyState: document.querySelector("#emptyState"),
  tableWrap: document.querySelector("#tableWrap"),
  profileTableBody: document.querySelector("#profileTableBody"),

  queueSummary: document.querySelector("#queueSummary"),
  queueSearchInput: document.querySelector("#queueSearchInput"),
  queueStatusFilter: document.querySelector("#queueStatusFilter"),
  queueEmptyState: document.querySelector("#queueEmptyState"),
  queueTableWrap: document.querySelector("#queueTableWrap"),
  queueTableBody: document.querySelector("#queueTableBody"),
  accountsGrid: document.querySelector("#accountsGrid"),

  youtubeTabCount: document.querySelector("#youtubeTabCount"),
  youtubeResearchForm: document.querySelector("#youtubeResearchForm"),
  youtubeKeywordInput: document.querySelector("#youtubeKeywordInput"),
  youtubeStartButton: document.querySelector("#youtubeStartButton"),
  youtubeStartButtonText: document.querySelector("#youtubeStartButtonText"),
  youtubeJobBadge: document.querySelector("#youtubeJobBadge"),
  youtubeProgressText: document.querySelector("#youtubeProgressText"),
  youtubeProgressBar: document.querySelector("#youtubeProgressBar"),
  youtubeStageText: document.querySelector("#youtubeStageText"),
  youtubeResultCount: document.querySelector("#youtubeResultCount"),
  youtubeLastError: document.querySelector("#youtubeLastError"),
  youtubeResultSummary: document.querySelector("#youtubeResultSummary"),
  youtubeSearchInput: document.querySelector("#youtubeSearchInput"),
  youtubeKeywordFilter: document.querySelector("#youtubeKeywordFilter"),
  youtubeLocationFilter: document.querySelector("#youtubeLocationFilter"),
  youtubeEmailFilter: document.querySelector("#youtubeEmailFilter"),
  youtubeSubscriberFilter: document.querySelector("#youtubeSubscriberFilter"),
  youtubeSortSelect: document.querySelector("#youtubeSortSelect"),
  youtubeEmptyState: document.querySelector("#youtubeEmptyState"),
  youtubeTableWrap: document.querySelector("#youtubeTableWrap"),
  youtubeTableBody: document.querySelector("#youtubeTableBody"),

    // OUTREACH
  outreachConnectForm:
    document.querySelector("#outreachConnectForm"),

  outreachUrlInput:
    document.querySelector("#outreachUrlInput"),
  outreachCompanyInput:
    document.querySelector("#outreachCompanyInput"),
  outreachCompanyMatch:
    document.querySelector("#outreachCompanyMatch"),

  outreachCampaignSelect:
    document.querySelector("#outreachCampaignSelect"),
  outreachCampaignTrigger:
    document.querySelector("#outreachCampaignTrigger"),
  outreachCampaignMenu:
    document.querySelector("#outreachCampaignMenu"),
  outreachCampaignValue:
    document.querySelector("#outreachCampaignValue"),
  outreachNewCampaignField:
    document.querySelector("#outreachNewCampaignField"),
  outreachNewCampaign:
    document.querySelector("#outreachNewCampaign"),
  outreachBatchName:
    document.querySelector("#outreachBatchName"),
  connectHistoryCampaignFilter:
    document.querySelector("#connectHistoryCampaignFilter"),
  connectHistoryCampaignTrigger:
    document.querySelector("#connectHistoryCampaignTrigger"),
  connectHistoryCampaignMenu:
    document.querySelector("#connectHistoryCampaignMenu"),
  connectHistoryCampaignValue:
    document.querySelector("#connectHistoryCampaignValue"),
  connectHistoryDateFilter:
    document.querySelector("#connectHistoryDateFilter"),
  connectHistoryDateTrigger:
    document.querySelector("#connectHistoryDateTrigger"),
  connectHistoryDateMenu:
    document.querySelector("#connectHistoryDateMenu"),
  connectHistoryDateValue:
    document.querySelector("#connectHistoryDateValue"),

  connectHistoryWeeks:
    document.querySelector("#connectHistoryWeeks"),

  connectHistoryCount:
    document.querySelector("#connectHistoryCount"),

  outreachStartButton:
    document.querySelector("#outreachStartButton"),

  outreachStartButtonText:
    document.querySelector("#outreachStartButtonText"),

  outreachDetectedCount:
    document.querySelector("#outreachDetectedCount"),

  outreachConnectExecutionSection:
    document.querySelector("#outreachConnectExecutionSection"),

  outreachJobResult:
    document.querySelector("#outreachJobResult"),

  outreachInputCount:
    document.querySelector("#outreachInputCount"),

  outreachReadyCount:
    document.querySelector("#outreachReadyCount"),

  outreachProcessedCount:
    document.querySelector("#outreachProcessedCount"),

  outreachSuccessCount:
    document.querySelector("#outreachSuccessCount"),

  outreachFailedCount:
    document.querySelector("#outreachFailedCount"),

  outreachDuplicateCount:
    document.querySelector("#outreachDuplicateCount"),

  outreachInvalidCount:
    document.querySelector("#outreachInvalidCount"),

  outreachProgressText:
    document.querySelector("#outreachProgressText"),

  outreachProgressBar:
    document.querySelector("#outreachProgressBar"),

  outreachProgressPercent:
    document.querySelector("#outreachProgressPercent"),

  outreachCreatedAt:
    document.querySelector("#outreachCreatedAt"),

  outreachStartedAt:
    document.querySelector("#outreachStartedAt"),

  outreachCompletedAt:
    document.querySelector("#outreachCompletedAt"),

  outreachJobMessage:
    document.querySelector("#outreachJobMessage"),

  outreachLastError:
    document.querySelector("#outreachLastError"),

  outreachCurrentTargetCount:
    document.querySelector("#outreachCurrentTargetCount"),

  outreachError:
    document.querySelector("#outreachError"),

  outreachSchedulerBadge:
    document.querySelector("#outreachSchedulerBadge"),

  outreachCurrentAccount:
    document.querySelector("#outreachCurrentAccount"),

  outreachUsedTurn:
    document.querySelector("#outreachUsedTurn"),

  outreachRemainingTurn:
    document.querySelector("#outreachRemainingTurn"),

  outreachSchedulerUpdatedAt:
    document.querySelector("#outreachSchedulerUpdatedAt"),

  outreachAccountCount:
    document.querySelector("#outreachAccountCount"),

  outreachAccountsList:
    document.querySelector("#outreachAccountsList"),

  outreachTotalRemaining:
    document.querySelector("#outreachTotalRemaining"),

  rateLimitAccountCardTemplate:
    document.querySelector("#rateLimitAccountCardTemplate"),

  rateLimitDrawerButton:
    document.querySelector("#rateLimitDrawerButton"),

  rateLimitSidebarBadge:
    document.querySelector("#rateLimitSidebarBadge"),

  rateLimitDrawer:
    document.querySelector("#rateLimitDrawer"),

  rateLimitDrawerBackdrop:
    document.querySelector("#rateLimitDrawerBackdrop"),

  rateLimitDrawerClose:
    document.querySelector("#rateLimitDrawerClose"),

  acceptanceInsightsDrawerButton:
    document.querySelector("#acceptanceInsightsDrawerButton"),

  acceptanceInsightsDrawer:
    document.querySelector("#acceptanceInsightsDrawer"),

  acceptanceInsightsDrawerBackdrop:
    document.querySelector("#acceptanceInsightsDrawerBackdrop"),

  acceptanceInsightsDrawerClose:
    document.querySelector("#acceptanceInsightsDrawerClose"),

  acceptanceInsightsScopeFilter:
    document.querySelector("#acceptanceInsightsScopeFilter"),

  acceptanceInsightsWeekField:
    document.querySelector("#acceptanceInsightsWeekField"),

  acceptanceInsightsWeekFilter:
    document.querySelector("#acceptanceInsightsWeekFilter"),

  acceptanceInsightsJobField:
    document.querySelector("#acceptanceInsightsJobField"),

  acceptanceInsightsJobFilter:
    document.querySelector("#acceptanceInsightsJobFilter"),

  acceptanceInsightsBestAccount:
    document.querySelector("#acceptanceInsightsBestAccount"),

  acceptanceInsightsBestMeta:
    document.querySelector("#acceptanceInsightsBestMeta"),

  acceptanceInsightsTotalConnected:
    document.querySelector("#acceptanceInsightsTotalConnected"),

  acceptanceInsightsTotalAccepted:
    document.querySelector("#acceptanceInsightsTotalAccepted"),

  acceptanceInsightsOverallRate:
    document.querySelector("#acceptanceInsightsOverallRate"),

  acceptanceInsightsEmpty:
    document.querySelector("#acceptanceInsightsEmpty"),

  acceptanceInsightsTableWrap:
    document.querySelector("#acceptanceInsightsTableWrap"),

  acceptanceInsightsTableBody:
    document.querySelector("#acceptanceInsightsTableBody"),

  acceptanceInsightsRowTemplate:
    document.querySelector("#acceptanceInsightsRowTemplate"),

  outreachDashboardUpdatedAt:
    document.querySelector("#outreachDashboardUpdatedAt"),

  outreachHistoryEmpty:
    document.querySelector("#outreachHistoryEmpty"),

  outreachHistoryTableWrap:
    document.querySelector("#outreachHistoryTableWrap"),

  outreachHistoryBody:
    document.querySelector("#outreachHistoryBody"),

  outreachHistoryRowTemplate:
    document.querySelector("#outreachHistoryRowTemplate"),

  outreachHistoryCount:
    document.querySelector("#outreachHistoryCount"),

  outreachHistoryPagination:
    document.querySelector("#outreachHistoryPagination"),

  outreachHistoryPageMeta:
    document.querySelector("#outreachHistoryPageMeta"),

  outreachHistoryPrevPage:
    document.querySelector("#outreachHistoryPrevPage"),

  outreachHistoryNextPage:
    document.querySelector("#outreachHistoryNextPage"),

  outreachAcceptanceEmpty:
    document.querySelector("#outreachAcceptanceEmpty"),
  outreachAcceptanceCampaignSummary:
    document.querySelector("#outreachAcceptanceCampaignSummary"),
  outreachAcceptanceCampaignSummaryName:
    document.querySelector("#outreachAcceptanceCampaignSummaryName"),
  outreachAcceptanceCampaignSummaryBatches:
    document.querySelector("#outreachAcceptanceCampaignSummaryBatches"),
  outreachAcceptanceCampaignSummaryProspects:
    document.querySelector("#outreachAcceptanceCampaignSummaryProspects"),
  outreachAcceptanceCampaignSummaryAccepted:
    document.querySelector("#outreachAcceptanceCampaignSummaryAccepted"),
  outreachAcceptanceCampaignSummaryPending:
    document.querySelector("#outreachAcceptanceCampaignSummaryPending"),
  outreachAcceptanceCampaignSummaryFailed:
    document.querySelector("#outreachAcceptanceCampaignSummaryFailed"),

  outreachAcceptanceTableWrap:
    document.querySelector("#outreachAcceptanceTableWrap"),

  outreachAcceptanceBody:
    document.querySelector("#outreachAcceptanceBody"),

  outreachAcceptanceRowTemplate:
    document.querySelector("#outreachAcceptanceRowTemplate"),

  outreachAcceptanceDeleteSelectedButton:
    document.querySelector("#outreachAcceptanceDeleteSelectedButton"),

  outreachDeleteJobsModal:
    document.querySelector("#outreachDeleteJobsModal"),

  outreachDeleteJobsCloseButton:
    document.querySelector("#outreachDeleteJobsCloseButton"),

  outreachDeleteJobsCancelButton:
    document.querySelector("#outreachDeleteJobsCancelButton"),

  outreachDeleteJobsConfirmButton:
    document.querySelector("#outreachDeleteJobsConfirmButton"),

  outreachDeleteJobsSummary:
    document.querySelector("#outreachDeleteJobsSummary"),

  outreachDeleteJobsError:
    document.querySelector("#outreachDeleteJobsError"),

  outreachAcceptanceHistoryItemTemplate:
    document.querySelector("#outreachAcceptanceHistoryItemTemplate"),

  outreachAcceptancePagination:
    document.querySelector("#outreachAcceptancePagination"),

  outreachAcceptancePageMeta:
    document.querySelector("#outreachAcceptancePageMeta"),

  outreachAcceptancePrevPage:
    document.querySelector("#outreachAcceptancePrevPage"),

  outreachAcceptanceNextPage:
    document.querySelector("#outreachAcceptanceNextPage"),

  outreachAcceptanceWeekPicker:
    document.querySelector("#outreachAcceptanceWeekPicker"),
  outreachAcceptanceCampaignFilter:
    document.querySelector("#outreachAcceptanceCampaignFilter"),
  outreachAcceptanceCampaignTrigger:
    document.querySelector("#outreachAcceptanceCampaignTrigger"),
  outreachAcceptanceCampaignMenu:
    document.querySelector("#outreachAcceptanceCampaignMenu"),
  outreachAcceptanceCampaignValue:
    document.querySelector("#outreachAcceptanceCampaignValue"),

  outreachAcceptanceWeekButton:
    document.querySelector("#outreachAcceptanceWeekButton"),

  outreachAcceptanceWeekButtonLabel:
    document.querySelector("#outreachAcceptanceWeekButtonLabel"),

  outreachAcceptanceWeekMenu:
    document.querySelector("#outreachAcceptanceWeekMenu"),

  outreachAcceptedWeekPicker:
    document.querySelector("#outreachAcceptedWeekPicker"),

  outreachAcceptedWeekButton:
    document.querySelector("#outreachAcceptedWeekButton"),

  outreachAcceptedWeekButtonLabel:
    document.querySelector("#outreachAcceptedWeekButtonLabel"),

  outreachAcceptedWeekMenu:
    document.querySelector("#outreachAcceptedWeekMenu"),

  outreachAcceptedCampaignPicker:
    document.querySelector("#outreachAcceptedCampaignPicker"),

  outreachAcceptedCampaignButton:
    document.querySelector("#outreachAcceptedCampaignButton"),

  outreachAcceptedCampaignButtonLabel:
    document.querySelector("#outreachAcceptedCampaignButtonLabel"),

  outreachAcceptedCampaignMenu:
    document.querySelector("#outreachAcceptedCampaignMenu"),

  outreachAcceptanceHistoryModal:
    document.querySelector("#outreachAcceptanceHistoryModal"),

  outreachAcceptanceHistoryModalBackdrop:
    document.querySelector("#outreachAcceptanceHistoryModalBackdrop"),

  outreachAcceptanceHistoryModalClose:
    document.querySelector("#outreachAcceptanceHistoryModalClose"),

  outreachAcceptanceHistoryModalTitle:
    document.querySelector("#outreachAcceptanceHistoryModalTitle"),

  outreachAcceptanceHistoryModalEmpty:
    document.querySelector("#outreachAcceptanceHistoryModalEmpty"),

  outreachAcceptanceHistoryModalList:
    document.querySelector("#outreachAcceptanceHistoryModalList"),


  outreachAcceptedPoolPanel:
    document.querySelector("#outreachAcceptedPoolPanel"),

  outreachAcceptedPoolSummary:
    document.querySelector("#outreachAcceptedPoolSummary"),

  outreachAcceptedPoolEmpty:
    document.querySelector("#outreachAcceptedPoolEmpty"),

  outreachAcceptedPoolTableWrap:
    document.querySelector("#outreachAcceptedPoolTableWrap"),

  outreachAcceptedPoolBody:
    document.querySelector("#outreachAcceptedPoolBody"),

  outreachAcceptedPoolRowTemplate:
    document.querySelector("#outreachAcceptedPoolRowTemplate"),

  outreachAcceptedSelectedCount:
    document.querySelector("#outreachAcceptedSelectedCount"),

  outreachAcceptedPoolGroupTemplate:
    document.querySelector("#outreachAcceptedPoolGroupTemplate"),

  outreachAcceptedPoolCampaignTemplate:
    document.querySelector("#outreachAcceptedPoolCampaignTemplate"),

  outreachAcceptedSelectPage:
    document.querySelector("#outreachAcceptedSelectPage"),

  outreachAcceptedPagination:
    document.querySelector("#outreachAcceptedPagination"),

  outreachAcceptedPageMeta:
    document.querySelector("#outreachAcceptedPageMeta"),

  outreachAcceptedPrevPage:
    document.querySelector("#outreachAcceptedPrevPage"),

  outreachAcceptedNextPage:
    document.querySelector("#outreachAcceptedNextPage"),

  messagePreparationCount:
    document.querySelector("#messagePreparationCount"),

  messagePreparationHeadline:
    document.querySelector("#messagePreparationHeadline"),

  messagePreparationMeta:
    document.querySelector("#messagePreparationMeta"),

  messagePrepareSelectedButton:
    document.querySelector("#messagePrepareSelectedButton"),

  messagePrepareAllButton:
    document.querySelector("#messagePrepareAllButton"),

  messagePrepareConfirmModal:
    document.querySelector("#messagePrepareConfirmModal"),

  messagePrepareConfirmTitle:
    document.querySelector("#messagePrepareConfirmTitle"),

  messagePrepareConfirmMeta:
    document.querySelector("#messagePrepareConfirmMeta"),

  messagePrepareConfirmError:
    document.querySelector("#messagePrepareConfirmError"),

  messagePrepareConfirmCloseButton:
    document.querySelector("#messagePrepareConfirmCloseButton"),

  messagePrepareConfirmCancelButton:
    document.querySelector("#messagePrepareConfirmCancelButton"),

  messagePrepareConfirmButton:
    document.querySelector("#messagePrepareConfirmButton"),

  messagePreparationError:
    document.querySelector("#messagePreparationError"),

  messageBatchCount:
    document.querySelector("#messageBatchCount"),

  messageBatchSourceFilter:
    document.querySelector("#messageBatchSourceFilter"),

  messageBatchWeekPicker:
    document.querySelector("#messageBatchWeekPicker"),

  messageBatchWeekButton:
    document.querySelector("#messageBatchWeekButton"),

  messageBatchWeekButtonLabel:
    document.querySelector("#messageBatchWeekButtonLabel"),

  messageBatchWeekMenu:
    document.querySelector("#messageBatchWeekMenu"),

  messageBatchEmpty:
    document.querySelector("#messageBatchEmpty"),

  messageBatchList:
    document.querySelector("#messageBatchList"),

  messageBatchGridWrap:
    document.querySelector("#messageBatchGridWrap"),

  messageBatchPagination:
    document.querySelector("#messageBatchPagination"),

  messageBatchPageMeta:
    document.querySelector("#messageBatchPageMeta"),

  messageBatchPrevPage:
    document.querySelector("#messageBatchPrevPage"),

  messageBatchNextPage:
    document.querySelector("#messageBatchNextPage"),


  messageBatchRowTemplate:
    document.querySelector("#messageBatchRowTemplate"),

  messageSendModal:
    document.querySelector("#messageSendModal"),

  messageSendDialogMeta:
    document.querySelector("#messageSendDialogMeta"),

  messageTemplateInput:
    document.querySelector("#messageTemplateInput"),

  messageTemplateSaveButton:
    document.querySelector("#messageTemplateSaveButton"),

  messageTemplateStatus:
    document.querySelector("#messageTemplateStatus"),

  messageSendCampaignName:
    document.querySelector("#messageSendCampaignName"),

  messageSendError:
    document.querySelector("#messageSendError"),

  messageSendCloseButton:
    document.querySelector("#messageSendCloseButton"),

  messageSendCancelButton:
    document.querySelector("#messageSendCancelButton"),

  messageSendConfirmButton:
    document.querySelector("#messageSendConfirmButton"),

  outreachReplyTabCount:
    document.querySelector("#outreachReplyTabCount"),

  outreachReplyAccountTabs:
    document.querySelector("#outreachReplyAccountTabs"),

  outreachReplyError:
    document.querySelector("#outreachReplyError"),

  outreachReplyEmpty:
    document.querySelector("#outreachReplyEmpty"),

  outreachReplyList:
    document.querySelector("#outreachReplyList"),

  outreachReplyInbox:
    document.querySelector("#outreachReplyInbox"),

  outreachReplyConversation:
    document.querySelector("#outreachReplyConversation"),

  outreachReplyAccountCount:
    document.querySelector("#outreachReplyAccountCount"),

  pageEyebrow:
    document.querySelector("#pageEyebrow"),

  pageTitle:
    document.querySelector("#pageTitle"),

  pageSubtitle:
    document.querySelector("#pageSubtitle"),

    // DRAWER
  drawerBackdrop:
    document.querySelector("#drawerBackdrop"),

  detailDrawer:
    document.querySelector("#detailDrawer"),

  drawerName:
    document.querySelector("#drawerName"),

  drawerContent:
    document.querySelector("#drawerContent"),

  closeDrawerButton:
    document.querySelector("#closeDrawerButton")
};

const state = {
  workerActivity: null,
  workerActivityLoading: false,
  sessionStatuses: [],
  sessionStatusLoading: false,
  sessionStatusRealtimeChannel: null,
  sessionStatusRealtimeReady: false,
  profiles: [],
  filteredProfiles: [],
  sources: [],
  filteredSources: [],
  accounts: [],
  worker: null,
  youtubeJobs: [],
  youtubeChannels: [],
  activeYoutubeJob: null,
  youtubeSubmitting: false,
  youtubePollTimer: null,
  youtubeRealtimeChannel: null,
  youtubeRealtimeReloadTimer: null,
  outreachSubmitting: false,
  outreachCurrentJob: null,
  outreachScheduler: null,
  outreachAccounts: [],
  outreachRecentJobs: [],
  connectCampaigns: [],
  campaignPerformanceWindow: "all",
  campaignPerformanceFilter: "all",
  campaignPerformance: [],
  campaignPerformanceOptions: [],
  campaignPerformanceLoading: false,
  campaignPerformanceError: "",
  campaignPerformanceRequestId: 0,
  expandedCampaignId: null,
  selectedConnectHistoryJobId: null,
  expandedConnectWeekKey: null,
  acceptanceInsights: null,
  acceptanceInsightsLoading: false,
  acceptanceInsightsError: null,
  outreachProcessTab: "connect",
  outreachHistoryPage: 1,
  outreachHistoryPageSize: 5,
  outreachAcceptancePage: 1,
  outreachAcceptancePageSize: 10,
  outreachAcceptanceCampaign: "",
  messageBatchPage: 1,
  messageBatchPageSize: 8,
  messageBatchSourceFilter: "all",
  messageBatchWeekKey: null,
  outreachPollTimer: null,
  outreachDashboardLoading: false,
  outreachProfilesLoading: false,
  outreachRateLimitsLoading: false,
  outreachAcceptanceSubmittingJobIds: new Set(),
  outreachAcceptanceHistoryByJobId: new Map(),
  outreachAcceptanceHistoryLoadingJobIds: new Set(),
  outreachAcceptanceHistoryModalJobId: null,
  outreachAcceptanceSelectedDeleteJobIds: new Set(),
  outreachAcceptanceDeleteSubmitting: false,
  outreachAcceptedPool: {
    summary: {
      total: 0,
      not_sent: 0,
      sent: 0
    },
    items: []
  },
  outreachAcceptedPoolFilter: "all",
  outreachAcceptedCampaignId: "",
  outreachAcceptedPoolWeekKey: null,
  outreachAcceptanceWeekKey: null,
  outreachAcceptedPoolPage: 1,
  outreachAcceptedPoolPageSize: 15,
  outreachAcceptedSelectedProspectIds: new Set(),
  messagePreparation: {
    count: 0,
    items: []
  },
  messageBatches: [],
  messagePreparationSubmitting: false,
  messagePreparationSelectedSubmitting: false,
  messagePrepareConfirmMode: null,
  messageBatchQueueSubmittingIds: new Set(),
  messageSendSelectedBatchId: null,
  messageSendLoadVersion: 0,
  messageTemplateLoading: false,
  messageTemplateSaving: false,
  messageTemplateCanSave: false,
  outreachReplies: [],
  outreachReplyAccounts: [],
  outreachReplySelectedAccountId: null,
  outreachReplySelectedIdByAccount: {},
  outreachReplyDrafts: {},
  outreachReplySendErrors: {},
  outreachReplyNextOffsetByAccount: {},
  outreachReplyHasMoreByAccount: {},
  outreachReplyLoadedByAccount: {},
  outreachReplyLoadingMoreByAccount: {},
  outreachReplyLoadErrorByAccount: {},
  outreachReplyScrollByAccount: {},
  outreachReplyRequestGeneration: 0,
  outreachRepliesLoading: false,
  outreachReplyRefreshing: false,
  outreachReplyRevision: null,
  outreachReplyRevisionLoading: false,
  outreachReplySendSubmitting: false,
  outreachReplyLastScanLoading: false,
  outreachReplyLastScanInitialized: false,
  outreachReplyLastScanId: null,
  tableErrors: {},
  commandPending: false
};

function assertConfig() {
  const validUrl =
    typeof config.supabaseUrl === "string" &&
    config.supabaseUrl.startsWith("https://");

  const validKey =
    typeof config.supabasePublishableKey === "string" &&
    !config.supabasePublishableKey.includes("YOUR_");

  if (!validUrl || !validKey) {
    throw new Error(
      "Missing the Supabase URL or publishable/anon key in config.js."
    );
  }
}

assertConfig();

const client = window.supabase.createClient(
  config.supabaseUrl,
  config.supabasePublishableKey
);

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatDate(value) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(date);
}

function formatAge(value) {
  if (!value) return "No data";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Unknown";
  }

  const seconds = Math.max(
    0,
    Math.floor((Date.now() - date.getTime()) / 1000)
  );

  if (seconds < 60) return `${seconds}s ago`;

  const minutes = Math.floor(seconds / 60);

  if (minutes < 60) return `${minutes}m ago`;

  const hours = Math.floor(minutes / 60);

  if (hours < 24) return `${hours}h ago`;

  return `${Math.floor(hours / 24)}d ago`;
}

function isToday(value) {
  if (!value) return false;

  const date = new Date(value);
  const now = new Date();

  return (
    date.getFullYear() === now.getFullYear() &&
    date.getMonth() === now.getMonth() &&
    date.getDate() === now.getDate()
  );
}

function isComplete(profile) {
  return Boolean(
    profile.name &&
    profile.headline &&
    profile.location
  );
}

function getPostCaptions(profile) {
  return [
    profile.post_1_caption,
    profile.post_2_caption,
    profile.post_3_caption,
    profile.post_4_caption,
    profile.post_5_caption
  ]
    .map((caption) => String(caption || "").trim())
    .filter(Boolean);
}

function getInitials(name) {
  const text = String(name || "").trim();

  if (!text) return "—";

  return text
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() || "")
    .join("");
}

function getLatestSnapshots(rows) {
  const latestBySource = new Map();

  for (const row of rows) {
    if (!latestBySource.has(row.source_id)) {
      latestBySource.set(row.source_id, row);
    }
  }

  return Array.from(latestBySource.values());
}

function normaliseStatus(value) {
  return String(value || "unknown")
    .trim()
    .toLowerCase();
}

function statusLabel(value) {
  const status = normaliseStatus(value);

  const labels = {
    pending: "Pending",
    processing: "Processing",
    completed: "Completed",
    failed: "Failed",
    disabled: "Disabled",
    available: "Available",
    scanning: "Scanning",
    cooldown: "Cooldown",
    needs_login: "Needs login",
    error: "Error",
    starting: "Starting",
    idle: "Idle",
    stopping: "Stopping",
    offline: "Offline"
  };

  return labels[status] || status;
}

function statusBadge(value) {
  const status = normaliseStatus(value);

  return `
    <span class="status-badge status-${escapeHtml(status)}">
      ${escapeHtml(statusLabel(status))}
    </span>
  `;
}

function countByStatus(status) {
  return state.sources.filter(
    (source) => normaliseStatus(source.job_status) === status
  ).length;
}

async function safeQuery(name, queryPromise, fallback) {
  try {
    const result = await queryPromise;

    if (result.error) {
      throw result.error;
    }

    delete state.tableErrors[name];

    return result.data ?? fallback;
  } catch (error) {
    state.tableErrors[name] = error.message || String(error);
    return fallback;
  }
}


function updateWorkerControlButtons() {
  const workerStatus = normaliseStatus(
    state.worker?.status
  );

  const isPaused = workerStatus === "paused";

  els.stopScanButton.classList.toggle(
    "is-resume",
    isPaused
  );

  els.stopScanButtonText.textContent =
    isPaused
      ? "Resume scan"
      : "Stop scan";

  els.stopScanButton.disabled =
    state.commandPending ||
    !state.worker?.worker_id;

  els.killProcessButton.disabled =
    state.commandPending ||
    !state.worker?.worker_id ||
    !state.worker?.current_source_id;
}

async function sendWorkerCommand(command) {
  const workerId = String(
    state.worker?.worker_id || ""
  ).trim();

  if (!workerId) {
    throw new Error(
      "No active worker ID found."
    );
  }

  const labels = {
    kill_current: "stop the current scan",
    stop_scan: "pause the scanner",
    resume_scan: "resume the scanner"
  };

  const confirmed = window.confirm(
    `Confirm ${labels[command] || command}?`
  );

  if (!confirmed) {
    return;
  }

  state.commandPending = true;
  updateWorkerControlButtons();

  try {
    const response = await fetch(
      "/api/worker/commands",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          worker_id: workerId,
          command
        })
      }
    );

    const result = await response.json();

    if (!response.ok || !result.ok) {
      throw new Error(
        result.detail ||
        result.error ||
        "Could not send the worker command."
      );
    }

    els.globalError.hidden = false;
    els.globalError.innerHTML = `
      <strong>Command sent.</strong><br />
      ${escapeHtml(labels[command] || command)}
      — the worker will process it in a few seconds.
    `;

    window.setTimeout(
      loadDashboard,
      1500
    );
  } finally {
    state.commandPending = false;
    updateWorkerControlButtons();
  }
}



function formatCompactNumber(value, fallback = "—") {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return fallback;
  }

  return new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 1
  }).format(number);
}

function youtubeStageLabel(value) {
  const stage = normaliseStatus(value);

  const labels = {
    queued: "Queued",
    starting: "Starting",
    searching: "Searching YouTube",
    collecting_channels: "Collecting channels",
    scanning_channels: "Scanning channels",
    saving_results: "Saving results",
    completed: "Completed",
    failed: "Failed"
  };

  return labels[stage] || statusLabel(stage);
}

function youtubeBadgeClass(status) {
  const cleaned = normaliseStatus(status);

  if (cleaned === "completed") return "pill-green";
  if (cleaned === "failed") return "pill-red";
  if (cleaned === "pending") return "pill-amber";
  if (cleaned === "processing") return "pill-purple";

  return "pill-neutral";
}

async function fetchAllYoutubeRows(queryFactory, pageSize = 1000) {
  const rows = [];
  let from = 0;

  while (true) {
    const result = await queryFactory(
      from,
      from + pageSize - 1
    );

    if (result.error) {
      throw result.error;
    }

    const batch = result.data || [];
    rows.push(...batch);

    if (batch.length < pageSize) {
      break;
    }

    from += pageSize;
  }

  return rows;
}

function populateYoutubeFilterOptions() {
  const currentKeyword =
    els.youtubeKeywordFilter?.value || "all";
  const currentLocation =
    els.youtubeLocationFilter?.value || "all";

  const keywords = Array.from(
    new Set(
      (state.youtubeJobs || [])
        .map((job) => String(job.keyword || "").trim())
        .filter(Boolean)
    )
  ).sort((a, b) => a.localeCompare(b));

  const locations = Array.from(
    new Set(
      (state.youtubeChannels || [])
        .map((channel) => String(channel.location || "").trim())
        .filter(Boolean)
    )
  ).sort((a, b) => a.localeCompare(b));

  els.youtubeKeywordFilter.innerHTML = [
    '<option value="all">All keywords</option>',
    ...keywords.map(
      (keyword) =>
        `<option value="${escapeHtml(keyword)}">${escapeHtml(keyword)}</option>`
    )
  ].join("");

  els.youtubeLocationFilter.innerHTML = [
    '<option value="all">All locations</option>',
    ...locations.map(
      (location) =>
        `<option value="${escapeHtml(location)}">${escapeHtml(location)}</option>`
    )
  ].join("");

  els.youtubeKeywordFilter.value =
    keywords.includes(currentKeyword)
      ? currentKeyword
      : "all";

  els.youtubeLocationFilter.value =
    locations.includes(currentLocation)
      ? currentLocation
      : "all";
}

async function loadYoutubeResearch() {
  try {
    state.youtubeJobs = await fetchAllYoutubeRows(
      (from, to) =>
        client
          .from("youtube_scan_jobs")
          .select(
            "id,keyword,status,current_stage,progress_percent,max_results,result_count,last_error,created_at,updated_at,completed_at"
          )
          .order("created_at", { ascending: false })
          .range(from, to)
    );

    delete state.tableErrors.youtubeJobs;
    state.activeYoutubeJob =
      state.youtubeJobs[0] || null;
  } catch (error) {
    state.tableErrors.youtubeJobs =
      error.message || String(error);
    state.youtubeJobs = [];
    state.activeYoutubeJob = null;
  }

  try {
    state.youtubeChannels = await fetchAllYoutubeRows(
      (from, to) =>
        client
          .from("youtube_scan_channels")
          .select(
            "id,job_id,channel_url,channel_name,subscriber_count_text,subscriber_count,video_count_text,video_count,channel_description,location,email,email_status,total_views_text,total_views,channel_links,scan_status,scanned_at"
          )
          .order("scanned_at", { ascending: false })
          .range(from, to)
    );

    delete state.tableErrors.youtubeChannels;
  } catch (error) {
    state.tableErrors.youtubeChannels =
      error.message || String(error);
    state.youtubeChannels = [];
  }

  populateYoutubeFilterOptions();
  renderYoutubeResearch();
  updateYoutubePolling();
}

function renderYoutubeResearch() {
  const job = state.activeYoutubeJob;

  const jobsById = new Map(
    (state.youtubeJobs || []).map(
      (item) => [String(item.id), item]
    )
  );

  const channels = state.youtubeChannels || [];

  const searchValue = String(
    els.youtubeSearchInput?.value || ""
  ).trim().toLowerCase();

  const keywordFilter =
    els.youtubeKeywordFilter?.value || "all";
  const locationFilter =
    els.youtubeLocationFilter?.value || "all";
  const emailFilter =
    els.youtubeEmailFilter?.value || "all";
  const subscriberFilter =
    els.youtubeSubscriberFilter?.value || "all";

  const minSubscribers =
    subscriberFilter === "all"
      ? 0
      : Number(subscriberFilter);

  let filteredChannels = channels.filter(
    (channel) => {
      const channelJob = jobsById.get(
        String(channel.job_id || "")
      );

      const keyword = String(
        channelJob?.keyword || ""
      ).trim();

      const location = String(
        channel.location || ""
      ).trim();

      const hasEmail = Boolean(
        String(channel.email || "").trim()
      );

      if (
        searchValue &&
        ![
          channel.channel_name,
          channel.channel_url,
          channel.location,
          channel.email,
          keyword
        ]
          .map((value) =>
            String(value || "").toLowerCase()
          )
          .some((value) =>
            value.includes(searchValue)
          )
      ) {
        return false;
      }

      if (
        keywordFilter !== "all" &&
        keyword !== keywordFilter
      ) {
        return false;
      }

      if (
        locationFilter !== "all" &&
        location !== locationFilter
      ) {
        return false;
      }

      if (
        emailFilter === "available" &&
        !hasEmail
      ) {
        return false;
      }

      if (
        emailFilter === "missing" &&
        hasEmail
      ) {
        return false;
      }

      if (
        minSubscribers > 0 &&
        Number(channel.subscriber_count || 0) <
          minSubscribers
      ) {
        return false;
      }

      return true;
    }
  );

  const sortValue =
    els.youtubeSortSelect?.value || "newest";

  filteredChannels.sort((a, b) => {
    if (sortValue === "subscribers") {
      return Number(b.subscriber_count || 0) -
        Number(a.subscriber_count || 0);
    }

    if (sortValue === "views") {
      return Number(b.total_views || 0) -
        Number(a.total_views || 0);
    }

    if (sortValue === "name") {
      return String(a.channel_name || "")
        .localeCompare(
          String(b.channel_name || "")
        );
    }

    return (
      new Date(b.scanned_at || 0).getTime() -
      new Date(a.scanned_at || 0).getTime()
    );
  });

  if (els.youtubeTabCount) {
    els.youtubeTabCount.textContent =
      String(channels.length);
  }

  const youtubeError =
    state.tableErrors.youtubeJobs ||
    state.tableErrors.youtubeChannels ||
    "";

  if (youtubeError) {
    els.youtubeLastError.hidden = false;
    els.youtubeLastError.textContent =
      `Could not read YouTube data from Supabase: ${youtubeError}`;
  }

  if (!job) {
    els.youtubeJobBadge.className =
      "pill pill-neutral";
    els.youtubeJobBadge.textContent = "Idle";
    els.youtubeProgressText.textContent =
      "No job yet";
    els.youtubeProgressBar.style.width = "0%";
    els.youtubeStageText.textContent = "Idle";
    els.youtubeResultCount.textContent =
      `${channels.length} total channels`;
  } else {
    const progress = Math.max(
      0,
      Math.min(
        100,
        Number(job.progress_percent || 0)
      )
    );

    const latestCount = channels.filter(
      (channel) =>
        String(channel.job_id) ===
        String(job.id)
    ).length;

    els.youtubeJobBadge.className =
      `pill ${youtubeBadgeClass(job.status)}`;
    els.youtubeJobBadge.textContent =
      statusLabel(job.status);
    els.youtubeProgressText.textContent =
      `${progress}%`;
    els.youtubeProgressBar.style.width =
      `${progress}%`;
    els.youtubeStageText.textContent =
      youtubeStageLabel(
        job.current_stage || job.status
      );
    els.youtubeResultCount.textContent =
      `${Math.max(
        Number(job.result_count || 0),
        latestCount
      )} / ${Number(job.max_results || 40)} latest · ${channels.length} total`;

    const lastError = String(
      job.last_error || ""
    ).trim();

    if (lastError) {
      els.youtubeLastError.hidden = false;
      els.youtubeLastError.textContent =
        lastError;
    } else if (!youtubeError) {
      els.youtubeLastError.hidden = true;
      els.youtubeLastError.textContent = "";
    }
  }

  els.youtubeResultSummary.textContent =
    `${filteredChannels.length} / ${channels.length} channels shown`;

  els.youtubeStartButton.disabled =
    state.youtubeSubmitting ||
    normaliseStatus(job?.status) ===
      "processing" ||
    normaliseStatus(job?.status) ===
      "pending";

  els.youtubeStartButtonText.textContent =
    state.youtubeSubmitting
      ? "Creating job..."
      : "Start research";

  els.youtubeEmptyState.hidden =
    filteredChannels.length > 0;
  els.youtubeTableWrap.hidden =
    filteredChannels.length === 0;

  els.youtubeTableBody.innerHTML =
    filteredChannels
      .map((channel) => {
        const channelJob = jobsById.get(
          String(channel.job_id || "")
        );

        const keyword =
          channelJob?.keyword || "—";

        const links = Array.isArray(
          channel.channel_links
        )
          ? channel.channel_links
          : [];

        const linksHtml = links.length
          ? links
              .map((link) => `
                <a
                  class="youtube-link-chip"
                  href="${escapeHtml(link.url || "#")}"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  ${escapeHtml(link.title || "Link")}
                </a>
              `)
              .join("")
          : '<span class="table-muted">—</span>';

        const emailText = channel.email
          ? channel.email
          : statusLabel(
              channel.email_status ||
              "unavailable"
            );

        return `
          <tr>
            <td>
              <div class="youtube-channel-cell">
                <strong>${escapeHtml(
                  channel.channel_name ||
                  "Unnamed channel"
                )}</strong>
                <a
                  href="${escapeHtml(
                    channel.channel_url || "#"
                  )}"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  ${escapeHtml(
                    channel.channel_url || "—"
                  )}
                </a>
              </div>
            </td>
            <td>
              <span class="youtube-keyword-chip">
                ${escapeHtml(keyword)}
              </span>
            </td>
            <td>${escapeHtml(
              channel.subscriber_count_text ||
              formatCompactNumber(
                channel.subscriber_count
              )
            )}</td>
            <td>${escapeHtml(
              channel.video_count_text ||
              formatCompactNumber(
                channel.video_count
              )
            )}</td>
            <td>${escapeHtml(
              channel.location || "—"
            )}</td>
            <td>${escapeHtml(emailText)}</td>
            <td>${escapeHtml(
              channel.total_views_text ||
              formatCompactNumber(
                channel.total_views
              )
            )}</td>
            <td>
              <div class="youtube-link-list">
                ${linksHtml}
              </div>
            </td>
            <td>${escapeHtml(
              formatDate(channel.scanned_at)
            )}</td>
          </tr>
        `;
      })
      .join("");
}

async function createYoutubeResearchJob(event) {
  event.preventDefault();

  const keyword = String(
    els.youtubeKeywordInput.value || ""
  ).trim();

  if (!keyword) {
    window.alert("Enter a YouTube keyword.");
    return;
  }

  state.youtubeSubmitting = true;
  renderYoutubeResearch();

  try {
    const response = await fetch(
      "/api/youtube/jobs",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          keyword,
          max_results: 40
        })
      }
    );

    const result = await response.json();

    if (!response.ok || !result.ok) {
      throw new Error(
        result.detail ||
        result.error ||
        "Could not create the YouTube research job."
      );
    }

    els.youtubeKeywordInput.value = "";
    await loadYoutubeResearch();
  } catch (error) {
    window.alert(error.message || String(error));
  } finally {
    state.youtubeSubmitting = false;
    renderYoutubeResearch();
  }
}

// =========================================================
// OUTREACH
// =========================================================


const OUTREACH_ACTIVE_POLL_INTERVAL_MS = 5000;
const OUTREACH_IDLE_POLL_INTERVAL_MS = 45000;
const OUTREACH_MAX_CONNECT_URLS = 150;
const NEW_CONNECT_CAMPAIGN = "__new__";
const connectDropdowns = [
  {
    select: els.outreachCampaignSelect,
    trigger: els.outreachCampaignTrigger,
    menu: els.outreachCampaignMenu,
    value: els.outreachCampaignValue,
    description: (option) => option.value === NEW_CONNECT_CAMPAIGN
      ? "Name a new group for future batches"
      : option.value ? "Add a batch to this campaign" : "Choose a group before adding profiles",
    icon: (option) => option.value === NEW_CONNECT_CAMPAIGN ? "+" : "▦"
  },
  {
    select: els.connectHistoryCampaignFilter,
    trigger: els.connectHistoryCampaignTrigger,
    menu: els.connectHistoryCampaignMenu,
    value: els.connectHistoryCampaignValue,
    description: (option) => option.value
      ? "Show this campaign's recent batches" : "Show batches from every campaign",
    icon: () => "▦"
  },
  {
    select: els.outreachAcceptanceCampaignFilter,
    trigger: els.outreachAcceptanceCampaignTrigger,
    menu: els.outreachAcceptanceCampaignMenu,
    value: els.outreachAcceptanceCampaignValue,
    description: (option) => option.value
      ? "Show acceptance results for this campaign" : "Show acceptance results from every campaign",
    icon: () => "▦"
  },
  {
    select: document.querySelector("#campaignPerformanceFilter"),
    trigger: document.querySelector("#campaignPerformanceFilterTrigger"),
    menu: document.querySelector("#campaignPerformanceFilterMenu"),
    value: document.querySelector("#campaignPerformanceFilterValue"),
    description: (option) => option.value === "all"
      ? "Show performance for every campaign" : "Show performance for this campaign",
    icon: () => "▦"
  },
  {
    select: els.connectHistoryDateFilter,
    trigger: els.connectHistoryDateTrigger,
    menu: els.connectHistoryDateMenu,
    value: els.connectHistoryDateValue,
    description: (option) => option.value
      ? "Show Connect batches from this day" : "Show every day in this campaign",
    icon: () => "▦"
  }
];

function closeConnectDropdown(dropdown, restoreFocus = false) {
  if (!dropdown.menu || !dropdown.trigger) return;
  dropdown.menu.hidden = true;
  dropdown.trigger.setAttribute("aria-expanded", "false");
  if (restoreFocus) dropdown.trigger.focus();
}

function renderConnectDropdown(dropdown) {
  const { select, trigger, menu, value } = dropdown;
  if (!select || !trigger || !menu || !value) return;
  const options = [...select.options];
  const selected = options.find((option) => option.value === select.value) || options[0];
  value.textContent = selected?.textContent || "";
  trigger.classList.toggle("is-placeholder", !select.value);
  const signature = JSON.stringify(options.map((option) => [option.value, option.textContent]));
  if (menu.dataset.optionsSignature !== signature) {
    menu.replaceChildren();
    for (const option of options) {
      const item = document.createElement("button");
      item.type = "button";
      item.className = "connect-custom-select-option";
      item.setAttribute("role", "menuitemradio");
      item.dataset.value = option.value;
      const icon = document.createElement("span");
      icon.className = "connect-custom-select-icon";
      icon.setAttribute("aria-hidden", "true");
      icon.textContent = dropdown.icon(option);
      const copy = document.createElement("span");
      copy.className = "connect-custom-select-copy";
      const title = document.createElement("strong");
      title.textContent = option.textContent;
      const description = document.createElement("small");
      description.textContent = dropdown.description(option);
      copy.append(title, description);
      item.append(icon, copy);
      item.addEventListener("click", () => {
        select.value = option.value;
        select.dispatchEvent(new Event("change", { bubbles: true }));
        closeConnectDropdown(dropdown, true);
      });
      menu.append(item);
    }
    menu.dataset.optionsSignature = signature;
  }
  for (const item of menu.querySelectorAll(".connect-custom-select-option")) {
    const active = item.dataset.value === select.value;
    item.classList.toggle("is-selected", active);
    item.setAttribute("aria-checked", String(active));
  }
}

function setupConnectDropdown(dropdown) {
  if (!dropdown.trigger || !dropdown.menu) return;
  renderConnectDropdown(dropdown);
  dropdown.trigger.addEventListener("click", () => {
    const opening = dropdown.menu.hidden;
    for (const other of connectDropdowns) closeConnectDropdown(other);
    dropdown.menu.hidden = !opening;
    dropdown.trigger.setAttribute("aria-expanded", String(opening));
  });
  dropdown.trigger.addEventListener("keydown", (event) => {
    if (event.key !== "ArrowDown" && event.key !== "ArrowUp") return;
    event.preventDefault();
    dropdown.menu.hidden = false;
    dropdown.trigger.setAttribute("aria-expanded", "true");
    const items = dropdown.menu.querySelectorAll(".connect-custom-select-option");
    (event.key === "ArrowDown" ? items[0] : items[items.length - 1])?.focus();
  });
  dropdown.menu.addEventListener("keydown", (event) => {
    const items = [...dropdown.menu.querySelectorAll(".connect-custom-select-option")];
    if (event.key === "Escape") {
      event.preventDefault();
      closeConnectDropdown(dropdown, true);
    } else if (["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) {
      event.preventDefault();
      const index = items.indexOf(document.activeElement);
      const next = event.key === "Home" ? 0 : event.key === "End" ? items.length - 1
        : (index + (event.key === "ArrowDown" ? 1 : -1) + items.length) % items.length;
      items[next]?.focus();
    }
  });
}
const OUTREACH_ACCOUNT_DISPLAY_NAMES = {
  outreach_account_01: "Minh Anh",
  outreach_account_02: "Trang Liu",
  outreach_account_03: "Minh Ánh",
  outreach_account_04: "Linh Giang",
  outreach_account_05: "Huyền Linh",
  outreach_account_06: "Frank Nguyen",
  outreach_account_07: "Phoebe"
};

function getOutreachAccountDisplayName(accountId) {
  return (
    OUTREACH_ACCOUNT_DISPLAY_NAMES[accountId] ||
    accountId ||
    "—"
  );
}

// ---------------------------------------------------------
// URL INPUT
// ---------------------------------------------------------


function parseOutreachUrls() {
  return parseOutreachInput().urls;
}

function parseOutreachInput() {
  return ConnectInput.parse(els.outreachUrlInput?.value, els.outreachCompanyInput?.value);
}

function selectedConnectCampaign() {
  const selected = els.outreachCampaignSelect?.value || "";
  return selected === NEW_CONNECT_CAMPAIGN
    ? (els.outreachNewCampaign?.value || "").trim()
    : selected;
}

function renderConnectCampaignSelection() {
  const isNew = els.outreachCampaignSelect?.value === NEW_CONNECT_CAMPAIGN;
  if (els.outreachNewCampaignField) els.outreachNewCampaignField.hidden = !isNew;
  if (els.outreachNewCampaign) els.outreachNewCampaign.required = isNew;
  if (els.outreachUrlInput) els.outreachUrlInput.disabled = !selectedConnectCampaign();
  if (els.outreachCompanyInput) els.outreachCompanyInput.disabled = !selectedConnectCampaign();
  renderConnectDropdown(connectDropdowns[0]);
  renderOutreachSubmittingState();
}

function renderConnectCampaignOptions(preferredName = "") {
  const select = els.outreachCampaignSelect;
  if (!select) return;
  const previous = select.value;
  select.replaceChildren(new Option("Select a campaign", ""));
  for (const name of state.connectCampaigns) select.add(new Option(name, name));
  select.add(new Option("+ Create new campaign…", NEW_CONNECT_CAMPAIGN));
  const choice = preferredName || previous;
  select.value = [...select.options].some((option) => option.value === choice) ? choice : "";
  renderConnectCampaignSelection();
}

async function loadConnectCampaigns(preferredName = "") {
  try {
    const response = await fetch("/api/outreach/connect/campaigns");
    const result = await response.json();
    if (!response.ok || !result.ok) throw new Error(result.error || "Campaigns unavailable");
    state.connectCampaigns = Array.isArray(result.campaigns) ? result.campaigns : [];
    renderConnectCampaignOptions(preferredName);
  } catch (error) {
    console.error("Could not load Connect campaigns:", error);
  }
}

function updateOutreachDetectedCount() {
  const {urls, companyNames, error} = parseOutreachInput();
  const overLimit = urls.length > OUTREACH_MAX_CONNECT_URLS;

  if (els.outreachDetectedCount) {
    els.outreachDetectedCount.textContent = overLimit
      ? `${urls.length} URLs detected — maximum ${OUTREACH_MAX_CONNECT_URLS}`
      : `${urls.length} / ${OUTREACH_MAX_CONNECT_URLS} URLs detected`;
    els.outreachDetectedCount.classList.toggle("is-over-limit", overLimit);
  }

  els.outreachUrlInput?.setAttribute("aria-invalid", String(overLimit));
  els.outreachCompanyInput?.setAttribute("aria-invalid", String(Boolean(error)));
  if (els.outreachCompanyMatch) {
    els.outreachCompanyMatch.hidden = !companyNames;
    els.outreachCompanyMatch.textContent = error || (companyNames ? `${companyNames.length} companies matched by row` : "");
    els.outreachCompanyMatch.classList.toggle("is-error", Boolean(error));
  }
  renderOutreachSubmittingState();
}


// ---------------------------------------------------------
// SUBMIT BUTTON
// ---------------------------------------------------------


function renderOutreachSubmittingState() {
  if (!els.outreachStartButton) {
    return;
  }

  els.outreachStartButton.disabled =
    state.outreachSubmitting ||
    !selectedConnectCampaign() ||
    Boolean(parseOutreachInput().error) ||
    parseOutreachUrls().length > OUTREACH_MAX_CONNECT_URLS;

  if (els.outreachStartButtonText) {
    els.outreachStartButtonText.textContent =
      state.outreachSubmitting
        ? "Creating job..."
        : "Start Connect";
  }
}


// ---------------------------------------------------------
// STATUS
// ---------------------------------------------------------


function getOutreachPillClass(status) {
  const normalized = String(
    status || ""
  ).toLowerCase();

  if (normalized === "completed") {
    return "pill-green";
  }

  if (normalized === "failed") {
    return "pill-red";
  }

  if (normalized === "running") {
    return "pill-purple";
  }

  if (normalized === "pending") {
    return "pill-amber";
  }

  return "pill-neutral";
}


// ---------------------------------------------------------
// CURRENT JOB
// ---------------------------------------------------------


function renderOutreachJob(job) {
  if (!els.outreachJobResult) {
    return;
  }

  if (els.outreachConnectExecutionSection) {
    els.outreachConnectExecutionSection.hidden = !job;
  }

  if (!job) {
    els.outreachJobResult.hidden = true;
    return;
  }

  els.outreachJobResult.hidden = false;

  const targetCount =
    Number(job.target_count || 0);

  const processedCount =
    Number(job.processed_count || 0);

  let progressPercent =
    Number(job.progress_percent || 0);

  if (
    !Number.isFinite(progressPercent) ||
    progressPercent < 0
  ) {
    progressPercent = 0;
  }

  progressPercent = Math.min(
    100,
    progressPercent
  );

  if (els.outreachInputCount) {
    els.outreachInputCount.textContent =
      String(job.input_count ?? 0);
  }

  if (els.outreachReadyCount) {
    els.outreachReadyCount.textContent =
      String(targetCount);
  }

  if (els.outreachProcessedCount) {
    els.outreachProcessedCount.textContent =
      String(processedCount);
  }

  if (els.outreachSuccessCount) {
    els.outreachSuccessCount.textContent =
      String(job.success_count ?? 0);
  }

  if (els.outreachFailedCount) {
    els.outreachFailedCount.textContent =
      String(job.failed_count ?? 0);
  }

  if (els.outreachDuplicateCount) {
    els.outreachDuplicateCount.textContent =
      String(job.duplicate_count ?? 0);
  }

  if (els.outreachInvalidCount) {
    els.outreachInvalidCount.textContent =
      String(job.invalid_count ?? 0);
  }

  if (els.outreachProgressText) {
    els.outreachProgressText.textContent =
      `${processedCount} / ${targetCount}`;
  }

  if (els.outreachProgressBar) {
    els.outreachProgressBar.style.width =
      `${progressPercent}%`;
  }

  if (els.outreachProgressPercent) {
    els.outreachProgressPercent.textContent =
      `${progressPercent}%`;
  }

  if (els.outreachCreatedAt) {
    els.outreachCreatedAt.textContent =
      formatDate(job.created_at);
  }

  if (els.outreachStartedAt) {
    els.outreachStartedAt.textContent =
      formatDate(job.started_at);
  }

  if (els.outreachCompletedAt) {
    els.outreachCompletedAt.textContent =
      formatDate(job.completed_at);
  }

  if (els.outreachJobMessage) {
    els.outreachJobMessage.textContent =
      (
        `${processedCount}/${targetCount} processed`
        + ` · ${job.success_count ?? 0} success`
        + ` · ${job.failed_count ?? 0} failed`
      );
  }

  if (els.outreachLastError) {
    const lastError = String(
      job.last_error || ""
    ).trim();

    els.outreachLastError.hidden =
      !lastError;

    els.outreachLastError.textContent =
      lastError;
  }

  if (els.outreachCurrentTargetCount) {
    els.outreachCurrentTargetCount.textContent =
      `${targetCount} profiles`;
  }
}


// ---------------------------------------------------------
// SCHEDULER
// ---------------------------------------------------------


function renderOutreachScheduler(
  scheduler
) {
  if (!scheduler) {
    if (els.outreachSchedulerBadge) {
      els.outreachSchedulerBadge.textContent =
        "No data";

      els.outreachSchedulerBadge.className =
        "pill pill-neutral";
    }

    if (els.outreachCurrentAccount) {
      els.outreachCurrentAccount.textContent =
        "—";
    }

    if (els.outreachUsedTurn) {
      els.outreachUsedTurn.textContent =
        "0 / 0";
    }

    if (els.outreachRemainingTurn) {
      els.outreachRemainingTurn.textContent =
        "0";
    }

    if (els.outreachSchedulerUpdatedAt) {
      els.outreachSchedulerUpdatedAt.textContent =
        "—";
    }

    return;
  }


  const used =
    Number(
      scheduler.used_in_current_turn || 0
    );

  const limit =
    Number(
      scheduler.turn_limit || 0
    );

  const remaining =
    Number(
      scheduler.remaining_in_current_turn || 0
    );


  if (els.outreachSchedulerBadge) {
    els.outreachSchedulerBadge.textContent =
      `${used}/${limit}`;

    els.outreachSchedulerBadge.className =
      "pill pill-purple";
  }


  if (els.outreachCurrentAccount) {
    els.outreachCurrentAccount.textContent =
      getOutreachAccountDisplayName(
        scheduler.current_account_id
      );
  }

  if (els.outreachUsedTurn) {
    els.outreachUsedTurn.textContent =
      `${used} / ${limit}`;
  }


  if (els.outreachRemainingTurn) {
    els.outreachRemainingTurn.textContent =
      String(remaining);
  }


  if (els.outreachSchedulerUpdatedAt) {
    els.outreachSchedulerUpdatedAt.textContent =
      formatDate(
        scheduler.updated_at
      );
  }
}


function openRateLimitDrawer() {
  if (!els.rateLimitDrawer) {
    return;
  }

  closeAcceptanceInsightsDrawer();

  void loadOutreachRateLimits();

  els.rateLimitDrawer.classList.add(
    "is-open"
  );

  els.rateLimitDrawer.setAttribute(
    "aria-hidden",
    "false"
  );

  els.rateLimitDrawerButton?.setAttribute(
    "aria-expanded",
    "true"
  );

  document.body.classList.add(
    "has-rate-limit-drawer-open"
  );
}


function closeRateLimitDrawer() {
  if (!els.rateLimitDrawer) {
    return;
  }

  els.rateLimitDrawer.classList.remove(
    "is-open"
  );

  els.rateLimitDrawer.setAttribute(
    "aria-hidden",
    "true"
  );

  els.rateLimitDrawerButton?.setAttribute(
    "aria-expanded",
    "false"
  );

  document.body.classList.remove(
    "has-rate-limit-drawer-open"
  );
}


function formatAcceptancePercent(
  value
) {
  const number = Number(
    value || 0
  );

  if (!Number.isFinite(number)) {
    return "0.0%";
  }

  return `${(
    number * 100
  ).toFixed(1)}%`;
}


function populateAcceptanceInsightsJobFilter() {
  if (!els.acceptanceInsightsJobFilter) {
    return;
  }

  const currentValue =
    els.acceptanceInsightsJobFilter.value ||
    "all";

  const fragment =
    document.createDocumentFragment();

  const allOption =
    document.createElement("option");

  allOption.value = "all";
  allOption.textContent =
    "All Connect Jobs";

  fragment.append(
    allOption
  );

  const apiJobs =
    Array.isArray(
      state.acceptanceInsights?.jobs
    )
      ? state.acceptanceInsights.jobs
      : [];

  const fallbackJobs =
    Array.isArray(
      state.outreachRecentJobs
    )
      ? state.outreachRecentJobs
      : [];

  const sourceJobs =
    apiJobs.length
      ? apiJobs
      : fallbackJobs;

  sourceJobs.forEach((job) => {
    const jobId = String(
      job.job_id ||
      job.id ||
      ""
    ).trim();

    if (!jobId) {
      return;
    }

    const option =
      document.createElement(
        "option"
      );

    option.value = jobId;
    option.textContent =
      String(
        getConnectCampaignLabel(job) ||
        jobId
      );

    fragment.append(
      option
    );
  });

  els.acceptanceInsightsJobFilter
    .replaceChildren(
      fragment
    );

  const stillExists = Array.from(
    els.acceptanceInsightsJobFilter.options
  ).some(
    (option) =>
      option.value === currentValue
  );

  els.acceptanceInsightsJobFilter.value =
    stillExists
      ? currentValue
      : "all";
}


function getCurrentMondayIso() {
  const now = new Date();

  const local = new Date(
    now.toLocaleString(
      "en-US",
      {
        timeZone: "Asia/Ho_Chi_Minh"
      }
    )
  );

  const day =
    local.getDay();

  const distance =
    day === 0
      ? 6
      : day - 1;

  local.setDate(
    local.getDate() - distance
  );

  const year =
    local.getFullYear();

  const month =
    String(
      local.getMonth() + 1
    ).padStart(
      2,
      "0"
    );

  const date =
    String(
      local.getDate()
    ).padStart(
      2,
      "0"
    );

  return `${year}-${month}-${date}`;
}


function populateAcceptanceInsightsWeekFilter() {
  if (!els.acceptanceInsightsWeekFilter) {
    return;
  }

  const currentValue =
    els.acceptanceInsightsWeekFilter.value ||
    "";

  const weeks =
    Array.isArray(
      state.acceptanceInsights?.weeks
    )
      ? state.acceptanceInsights.weeks
      : [];

  const fragment =
    document.createDocumentFragment();

  const fallbackMonday =
    getCurrentMondayIso();

  if (!weeks.length) {
    const option =
      document.createElement("option");

    option.value =
      fallbackMonday;

    option.textContent =
      "Current week";

    fragment.append(
      option
    );
  } else {
    weeks.forEach((week) => {
      const value =
        String(
          week.week_start ||
          ""
        ).trim();

      if (!value) {
        return;
      }

      const option =
        document.createElement("option");

      option.value =
        value;

      option.textContent =
        String(
          week.label ||
          value
        );

      fragment.append(
        option
      );
    });
  }

  els.acceptanceInsightsWeekFilter
    .replaceChildren(
      fragment
    );

  const options = Array.from(
    els.acceptanceInsightsWeekFilter.options
  );

  const stillExists =
    options.some(
      (option) =>
        option.value === currentValue
    );

  els.acceptanceInsightsWeekFilter.value =
    stillExists
      ? currentValue
      : (
          options[0]?.value ||
          fallbackMonday
        );
}


function syncAcceptanceInsightsFilters() {
  const scope =
    els.acceptanceInsightsScopeFilter?.value ||
    "all";

  const weekActive =
    scope === "week";

  const jobActive =
    scope === "job";

  if (els.acceptanceInsightsWeekField) {
    els.acceptanceInsightsWeekField.hidden =
      !weekActive;
  }

  if (els.acceptanceInsightsWeekFilter) {
    els.acceptanceInsightsWeekFilter.disabled =
      !weekActive;
  }

  if (els.acceptanceInsightsJobField) {
    els.acceptanceInsightsJobField.hidden =
      !jobActive;
  }

  if (els.acceptanceInsightsJobFilter) {
    els.acceptanceInsightsJobFilter.disabled =
      !jobActive;

    if (!jobActive) {
      els.acceptanceInsightsJobFilter.value =
        "all";
    }
  }
}


function renderAcceptanceInsights() {
  populateAcceptanceInsightsJobFilter();
  populateAcceptanceInsightsWeekFilter();
  syncAcceptanceInsightsFilters();

  const insights =
    state.acceptanceInsights;

  const loading =
    state.acceptanceInsightsLoading;

  const error =
    state.acceptanceInsightsError;

  const accounts =
    Array.isArray(
      insights?.accounts
    )
      ? insights.accounts
      : [];

  const summary =
    insights?.summary ||
    {};

  const best =
    summary.best_performer ||
    null;

  if (els.acceptanceInsightsBestAccount) {
    els.acceptanceInsightsBestAccount.textContent =
      best
        ? getOutreachAccountDisplayName(
            best.account_id
          )
        : "—";
  }

  if (els.acceptanceInsightsBestMeta) {
    els.acceptanceInsightsBestMeta.textContent =
      best
        ? `${Number(
            best.accepted || 0
          )} accepted · ${formatAcceptancePercent(
            best.acceptance_rate
          )}`
        : (
            loading
              ? "Loading performance data..."
              : "No accepted connections yet"
          );
  }

  if (els.acceptanceInsightsTotalConnected) {
    els.acceptanceInsightsTotalConnected.textContent =
      loading
        ? "…"
        : Number(
            summary.total_connected ||
            0
          ).toLocaleString(
            "vi-VN"
          );
  }

  if (els.acceptanceInsightsTotalAccepted) {
    els.acceptanceInsightsTotalAccepted.textContent =
      loading
        ? "…"
        : Number(
            summary.total_accepted ||
            0
          ).toLocaleString(
            "vi-VN"
          );
  }

  if (els.acceptanceInsightsOverallRate) {
    els.acceptanceInsightsOverallRate.textContent =
      loading
        ? "…"
        : formatAcceptancePercent(
            summary.overall_rate
          );
  }

  const hasRows =
    accounts.length > 0;

  if (els.acceptanceInsightsEmpty) {
    els.acceptanceInsightsEmpty.hidden =
      hasRows;

    if (!hasRows) {
      els.acceptanceInsightsEmpty.textContent =
        loading
          ? "Loading Acceptance Insights..."
          : error
            ? error
            : "No Connect data in this scope.";
    }
  }

  if (els.acceptanceInsightsTableWrap) {
    els.acceptanceInsightsTableWrap.hidden =
      !hasRows;
  }

  if (
    !els.acceptanceInsightsTableBody ||
    !els.acceptanceInsightsRowTemplate
  ) {
    return;
  }

  els.acceptanceInsightsTableBody
    .replaceChildren();

  accounts.forEach((row) => {
    const fragment =
      els.acceptanceInsightsRowTemplate
        .content
        .cloneNode(
          true
        );

    const setText = (
      selector,
      value
    ) => {
      const element =
        fragment.querySelector(
          selector
        );

      if (element) {
        element.textContent =
          String(value);
      }
    };

    setText(
      "[data-insights-account]",
      getOutreachAccountDisplayName(
        row.account_id
      )
    );

    setText(
      "[data-insights-connected]",
      Number(
        row.connected ||
        0
      ).toLocaleString(
        "vi-VN"
      )
    );

    setText(
      "[data-insights-accepted]",
      Number(
        row.accepted ||
        0
      ).toLocaleString(
        "vi-VN"
      )
    );

    setText(
      "[data-insights-rate]",
      formatAcceptancePercent(
        row.acceptance_rate
      )
    );

    setText(
      "[data-insights-share]",
      formatAcceptancePercent(
        row.share_of_total_accepted
      )
    );

    els.acceptanceInsightsTableBody
      .append(
        fragment
      );
  });
}


async function loadAcceptanceInsights() {
  if (
    state.acceptanceInsightsLoading
  ) {
    return;
  }

  state.acceptanceInsightsLoading =
    true;

  state.acceptanceInsightsError =
    null;

  renderAcceptanceInsights();

  const scope =
    els.acceptanceInsightsScopeFilter?.value ||
    "all";

  const selectedJobId =
    scope === "job"
      ? String(
          els.acceptanceInsightsJobFilter?.value ||
          ""
        ).trim()
      : "";

  const selectedWeekStart =
    scope === "week"
      ? String(
          els.acceptanceInsightsWeekFilter?.value ||
          getCurrentMondayIso()
        ).trim()
      : "";

  const params =
    new URLSearchParams();

  if (
    selectedJobId &&
    selectedJobId !== "all"
  ) {
    params.set(
      "job_id",
      selectedJobId
    );
  }

  if (selectedWeekStart) {
    params.set(
      "week_start",
      selectedWeekStart
    );
  }

  const query =
    params.toString()
      ? `?${params.toString()}`
      : "";

  try {
    const response = await fetch(
      `/api/outreach/acceptance-insights${query}`,
      {
        method: "GET",
        headers: {
          "Accept": "application/json"
        },
        cache: "no-store"
      }
    );

    const result =
      await response.json();

    if (
      !response.ok ||
      !result.ok
    ) {
      throw new Error(
        result.detail ||
        result.error ||
        "Could not load Acceptance Insights."
      );
    }

    state.acceptanceInsights =
      result.insights ||
      null;

  } catch (error) {
    state.acceptanceInsightsError =
      error.message ||
      String(error);

  } finally {
    state.acceptanceInsightsLoading =
      false;

    renderAcceptanceInsights();
  }
}


function openAcceptanceInsightsDrawer() {
  if (!els.acceptanceInsightsDrawer) {
    return;
  }

  closeRateLimitDrawer();

  // Never reopen with stale aggregate data.
  state.acceptanceInsights = null;
  state.acceptanceInsightsError = null;

  els.acceptanceInsightsDrawer.classList.add(
    "is-open"
  );

  els.acceptanceInsightsDrawer.setAttribute(
    "aria-hidden",
    "false"
  );

  els.acceptanceInsightsDrawerButton
    ?.setAttribute(
      "aria-expanded",
      "true"
    );

  document.body.classList.add(
    "has-acceptance-insights-drawer-open"
  );

  loadAcceptanceInsights();
}


function closeAcceptanceInsightsDrawer() {
  if (!els.acceptanceInsightsDrawer) {
    return;
  }

  els.acceptanceInsightsDrawer.classList.remove(
    "is-open"
  );

  els.acceptanceInsightsDrawer.setAttribute(
    "aria-hidden",
    "true"
  );

  els.acceptanceInsightsDrawerButton
    ?.setAttribute(
      "aria-expanded",
      "false"
    );

  document.body.classList.remove(
    "has-acceptance-insights-drawer-open"
  );
}

function renderRateLimitSidebarSummary(
  accounts
) {
  const rows =
    Array.isArray(accounts)
      ? accounts
      : [];

  if (
    !els.rateLimitSidebarBadge ||
    !els.rateLimitDrawerButton
  ) {
    return;
  }

  els.rateLimitDrawerButton.classList.remove(
    "is-warning",
    "is-critical"
  );

  if (!rows.length) {
    els.rateLimitSidebarBadge.textContent =
      "—";

    return;
  }

  let nearCap = 0;
  let exhausted = 0;

  rows.forEach((account) => {
    const weeklySent = Number(
      account.weekly_success_count || 0
    );

    const weeklyLimit = Math.max(
      1,
      Number(
        account.weekly_limit || 100
      )
    );

    const remaining = Number(
      account.weekly_remaining ?? (
        weeklyLimit - weeklySent
      )
    );

    if (
      remaining <= 0 ||
      account.quota_available === false
    ) {
      exhausted += 1;
      return;
    }

    if (
      weeklySent / weeklyLimit >= 0.8
    ) {
      nearCap += 1;
    }
  });

  const alertCount = exhausted + nearCap;

  if (alertCount > 0) {
    els.rateLimitSidebarBadge.textContent =
      `${alertCount}`;

    els.rateLimitDrawerButton.classList.add(
      "is-critical"
    );

    return;
  }

  els.rateLimitSidebarBadge.textContent =
    `${rows.length}`;
}


// ---------------------------------------------------------
// ACCOUNTS
// ---------------------------------------------------------
function getOutreachTargetPillClass(
  status
) {
  const normalized = String(
    status || ""
  ).toLowerCase();

  if (
    normalized === "completed" ||
    normalized === "invitation_sent" ||
    normalized === "already_connected"
  ) {
    return "pill-green";
  }

  if (normalized === "failed") {
    return "pill-red";
  }

  if (normalized === "running") {
    return "pill-purple";
  }

  if (normalized === "pending") {
    return "pill-amber";
  }

  return "pill-neutral";
}


function renderOutreachAccounts(
  accounts
) {
  const rows =
    Array.isArray(accounts)
      ? accounts
      : [];

  renderRateLimitSidebarSummary(
    rows
  );

  if (els.outreachTotalRemaining) {
    const totalCapacity = rows.reduce((sum, account) => sum + Number(account.weekly_limit || 100), 0);
    const totalUsed = rows.reduce(
      (sum, account) => sum + Math.max(
        0,
        Number(account.weekly_success_count || 0)
      ),
      0
    );
    const totalRemaining = Math.max(
      0,
      totalCapacity - totalUsed
    );
    els.outreachTotalRemaining.textContent =
      `${totalRemaining} / ${totalCapacity}`;
  }

  if (
    !els.outreachAccountsList ||
    !els.rateLimitAccountCardTemplate
  ) {
    return;
  }

  els.outreachAccountsList.replaceChildren();

  if (!rows.length) {
    const empty =
      document.createElement("div");

    empty.className =
      "outreach-job-empty";

    empty.textContent =
      "No account data available.";

    els.outreachAccountsList.append(
      empty
    );

    return;
  }

  rows.forEach((account) => {
    const fragment =
      els.rateLimitAccountCardTemplate
        .content
        .cloneNode(true);

    const card =
      fragment.querySelector(
        ".rate-limit-account-card"
      );

    const weeklySent =
      Number(
        account.weekly_success_count || 0
      );

    const weeklyLimit =
      Math.max(
        1,
        Number(
          account.weekly_limit || 100
        )
      );

    const weeklyRemaining =
      Math.max(
        0,
        Number(
          account.weekly_remaining ?? (
            weeklyLimit - weeklySent
          )
        )
      );

    const weeklyPercent =
      Math.max(
        0,
        Math.min(
          100,
          weeklySent /
          weeklyLimit *
          100
        )
      );

    const setText = (
      selector,
      value
    ) => {
      const element =
        fragment.querySelector(
          selector
        );

      if (element) {
        element.textContent =
          String(value);
      }
    };

    setText(
      "[data-rate-account-name]",
      getOutreachAccountDisplayName(
        account.account_id
      )
    );

    setText(
      "[data-rate-weekly-label]",
      `${weeklySent} / ${weeklyLimit}`
    );

    const progressBar =
      fragment.querySelector(
        "[data-rate-weekly-progress]"
      );

    if (progressBar) {
      progressBar.style.width =
        `${weeklyPercent}%`;
    }

    const progressTrack =
      fragment.querySelector(
        "[data-rate-progress-track]"
      );

    if (progressTrack) {
      progressTrack.setAttribute(
        "aria-valuenow",
        String(Math.round(weeklyPercent))
      );
      progressTrack.setAttribute(
        "aria-valuetext",
        `${weeklySent} of ${weeklyLimit} weekly connections used`
      );
    }

    card?.classList.toggle(
      "is-warning",
      weeklyPercent >= 80 && weeklyRemaining > 0
    );
    card?.classList.toggle(
      "is-limited",
      weeklyRemaining <= 0 || account.quota_available === false
    );

    els.outreachAccountsList.append(
      fragment
    );
  });
}


// ---------------------------------------------------------
// ACCEPTANCE CHECK
// ---------------------------------------------------------


function getOutreachAcceptanceLabel(
  acceptance
) {
  if (!acceptance) {
    return "Not checked";
  }

  const status = normaliseStatus(
    acceptance.status
  );

  if (status === "pending") {
    return "Queued";
  }

  if (status === "running") {
    return "Checking";
  }

  if (status === "completed") {
    return "Completed";
  }

  if (status === "failed") {
    return "Check failed";
  }

  return statusLabel(status);
}


async function queueOutreachAcceptanceCheck(
  jobId
) {
  const cleanedJobId = String(
    jobId || ""
  ).trim();

  if (!cleanedJobId) {
    throw new Error(
      "Outreach job ID not found."
    );
  }

  if (
    state
      .outreachAcceptanceSubmittingJobIds
      .has(cleanedJobId)
  ) {
    return;
  }

  state
    .outreachAcceptanceSubmittingJobIds
    .add(cleanedJobId);

  renderOutreachAcceptanceJobs(
    state.outreachRecentJobs
  );

  try {
    const response = await fetch(
      `/api/outreach/connect/jobs/${encodeURIComponent(
        cleanedJobId
      )}/check-acceptance`,
      {
        method: "POST",
        headers: {
          "Accept": "application/json"
        },
        cache: "no-store"
      }
    );

    let result = {};

    try {
      result = await response.json();
    } catch (error) {
      result = {};
    }

    if (
      !response.ok ||
      !result.ok
    ) {
      throw new Error(
        result.detail ||
        result.error ||
        "Could not queue the Acceptance Check."
      );
    }

    await loadOutreachDashboard();

  } finally {
    state
      .outreachAcceptanceSubmittingJobIds
      .delete(cleanedJobId);

    renderOutreachAcceptanceJobs(
      state.outreachRecentJobs
    );
  }
}


function getConnectCampaignLabel(job) {
  return String(job?.batch_label || job?.display_name || job?.job_code || job?.id || "").trim();
}

function getLatestAcceptanceCheckedAt(acceptance){if(!acceptance)return null;return acceptance.completed_at||acceptance.updated_at||acceptance.started_at||null}
function getAcceptanceDisplayStatus(acceptance){return acceptance?normaliseStatus(acceptance.status||"not_checked"):"not_checked"}
function getAcceptanceStatusLabel(acceptance){const s=getAcceptanceDisplayStatus(acceptance),n=Number(acceptance?.run_number||0);if(s==="not_checked")return"Not checked";const l=s==="pending"?"Queued":s==="running"?"Checking":s==="completed"?"Completed":s==="failed"?"Check failed":statusLabel(s);return n>0?`#${n} ${l}`:l}
function updateSimplePagination({container,meta,prev,next,currentPage,totalPages,totalItems,startIndex,pageLength}){if(!container)return;container.hidden=totalItems<=0;if(totalItems<=0)return;if(meta)meta.textContent=`Page ${currentPage} / ${totalPages} · ${startIndex+1}-${startIndex+pageLength} of ${totalItems}`;if(prev)prev.disabled=currentPage<=1;if(next)next.disabled=currentPage>=totalPages}
function renderOutreachHistory(jobs){const rows=Array.isArray(jobs)?jobs:[];if(els.outreachHistoryCount)els.outreachHistoryCount.textContent=`${rows.length} jobs`;if(!els.outreachHistoryEmpty||!els.outreachHistoryTableWrap||!els.outreachHistoryBody||!els.outreachHistoryRowTemplate)return;if(!rows.length){els.outreachHistoryEmpty.hidden=false;els.outreachHistoryTableWrap.hidden=true;els.outreachHistoryBody.replaceChildren();if(els.outreachHistoryPagination)els.outreachHistoryPagination.hidden=true;return}const ps=Number(state.outreachHistoryPageSize||5),tp=Math.max(1,Math.ceil(rows.length/ps));state.outreachHistoryPage=Math.min(tp,Math.max(1,state.outreachHistoryPage));const si=(state.outreachHistoryPage-1)*ps,pr=rows.slice(si,si+ps);els.outreachHistoryEmpty.hidden=true;els.outreachHistoryTableWrap.hidden=false;els.outreachHistoryBody.replaceChildren();pr.forEach(job=>{const f=els.outreachHistoryRowTemplate.content.cloneNode(true),s=normaliseStatus(job.status),vals={"[data-connect-job-code]":job.job_code||"—","[data-connect-job-profiles]":Number(job.target_count||0),"[data-connect-job-processed]":Number(job.processed_count||0),"[data-connect-job-success]":Number(job.success_count||0),"[data-connect-job-failed]":Number(job.failed_count||0),"[data-connect-job-created]":formatDate(job.created_at)};Object.entries(vals).forEach(([q,v])=>{const e=f.querySelector(q);if(e)e.textContent=String(v)});const se=f.querySelector("[data-connect-job-status]");if(se){se.textContent=statusLabel(s);se.className=`pill ${getOutreachPillClass(s)}`}els.outreachHistoryBody.append(f)});updateSimplePagination({container:els.outreachHistoryPagination,meta:els.outreachHistoryPageMeta,prev:els.outreachHistoryPrevPage,next:els.outreachHistoryNextPage,currentPage:state.outreachHistoryPage,totalPages:tp,totalItems:rows.length,startIndex:si,pageLength:pr.length})}

function getAcceptanceRunStatusLabel(
  run
) {
  const status = normaliseStatus(
    run?.status ||
    "unknown"
  );

  const number = Number(
    run?.run_number ||
    0
  );

  const label =
    status === "pending"
      ? "Queued"
      : status === "running"
        ? "Checking"
        : status === "completed"
          ? "Completed"
          : status === "failed"
            ? "Failed"
            : statusLabel(status);

  return number > 0
    ? `#${number} ${label}`
    : label;
}


async function loadAcceptanceCheckHistory(
  jobId
) {
  const cleanedJobId =
    String(
      jobId ||
      ""
    ).trim();

  if (
    !cleanedJobId ||
    state.outreachAcceptanceHistoryLoadingJobIds.has(
      cleanedJobId
    )
  ) {
    return;
  }

  state.outreachAcceptanceHistoryLoadingJobIds.add(
    cleanedJobId
  );

  if (state.outreachAcceptanceHistoryModalJobId === cleanedJobId) {
    renderAcceptanceHistoryModal();
  }

  try {
    const response = await fetch(
      `/api/outreach/connect/jobs/${encodeURIComponent(
        cleanedJobId
      )}/acceptance-checks`,
      {
        method: "GET",
        headers: {
          "Accept": "application/json"
        },
        cache: "no-store"
      }
    );

    const result =
      await response.json();

    if (
      !response.ok ||
      !result.ok
    ) {
      throw new Error(
        result.detail ||
        result.error ||
        "Could not load Acceptance Check history."
      );
    }

    state.outreachAcceptanceHistoryByJobId.set(
      cleanedJobId,
      Array.isArray(
        result.runs
      )
        ? result.runs
        : []
    );

  } catch (error) {
    state.outreachAcceptanceHistoryByJobId.set(
      cleanedJobId,
      {
        error:
          error.message ||
          String(error)
      }
    );

  } finally {
    state.outreachAcceptanceHistoryLoadingJobIds.delete(
      cleanedJobId
    );

    renderOutreachAcceptanceJobs(
      state.outreachRecentJobs
    );

    if (state.outreachAcceptanceHistoryModalJobId === cleanedJobId) {
      renderAcceptanceHistoryModal();
    }
  }
}


function renderAcceptanceHistoryModal() {
  const modal = els.outreachAcceptanceHistoryModal;
  const jobId = state.outreachAcceptanceHistoryModalJobId;

  if (!modal || !jobId) {
    return;
  }

  const job = state.outreachRecentJobs.find(
    (item) => String(item?.id || "").trim() === jobId
  );

  if (!job) {
    closeAcceptanceHistoryModal();
    return;
  }

  const cached = state.outreachAcceptanceHistoryByJobId.get(jobId);
  const loading = state.outreachAcceptanceHistoryLoadingJobIds.has(jobId);
  const error = cached && !Array.isArray(cached) ? cached.error : null;
  const runs = Array.isArray(cached) ? cached : [];

  if (els.outreachAcceptanceHistoryModalTitle) {
    els.outreachAcceptanceHistoryModalTitle.textContent =
      `${getConnectCampaignLabel(job) || "Connect Job"} · Check runs`;
  }

  const empty = els.outreachAcceptanceHistoryModalEmpty;
  const list = els.outreachAcceptanceHistoryModalList;

  if (!empty || !list) {
    return;
  }

  if (loading || error || !runs.length) {
    empty.hidden = false;
    empty.textContent = loading
      ? "Loading acceptance history..."
      : error || "No acceptance check runs yet.";
    list.hidden = true;
    list.replaceChildren();
    return;
  }

  empty.hidden = true;
  list.hidden = false;
  list.replaceChildren();

  runs.forEach((run) => {
    const item = els.outreachAcceptanceHistoryItemTemplate?.content.cloneNode(true);

    if (!item) {
      return;
    }

    const setText = (selector, value) => {
      const element = item.querySelector(selector);

      if (element) {
        element.textContent = String(value);
      }
    };

    const status = normaliseStatus(run.status);
    const badge = item.querySelector("[data-history-run-status]");

    if (badge) {
      badge.textContent = getAcceptanceRunStatusLabel(run);
      badge.className = `pill ${getOutreachPillClass(status)}`;
    }

    setText(
      "[data-history-run-time]",
      formatDate(run.completed_at || run.updated_at || run.started_at || run.created_at)
    );
    setText(
      "[data-history-checked]",
      `${Number(run.checked_count || 0)} / ${Number(run.total_to_check || 0)}`
    );
    setText("[data-history-accepted]", Number(run.new_accepted_count || 0));
    setText("[data-history-pending]", Number(run.still_pending_count || 0));
    setText(
      "[data-history-unknown]",
      Number(run.declined_or_unknown_count || 0)
    );
    setText("[data-history-failed]", Number(run.failed_count || 0));
    list.append(item);
  });
}


function openAcceptanceHistoryModal(job) {
  const jobId = String(job?.id || "").trim();

  if (!jobId || !els.outreachAcceptanceHistoryModal) {
    return;
  }

  state.outreachAcceptanceHistoryModalJobId = jobId;
  els.outreachAcceptanceHistoryModal.hidden = false;
  els.outreachAcceptanceHistoryModal.setAttribute("aria-hidden", "false");
  renderAcceptanceHistoryModal();

  if (
    !state.outreachAcceptanceHistoryByJobId.has(jobId) &&
    !state.outreachAcceptanceHistoryLoadingJobIds.has(jobId)
  ) {
    loadAcceptanceCheckHistory(jobId);
  }
}


function closeAcceptanceHistoryModal() {
  if (els.outreachAcceptanceHistoryModal) {
    els.outreachAcceptanceHistoryModal.hidden = true;
    els.outreachAcceptanceHistoryModal.setAttribute("aria-hidden", "true");
  }

  state.outreachAcceptanceHistoryModalJobId = null;
}


function updateAcceptanceDeleteSelectionUi() {
  const count =
    state.outreachAcceptanceSelectedDeleteJobIds.size;

  if (els.outreachAcceptanceDeleteSelectedButton) {
    els.outreachAcceptanceDeleteSelectedButton.disabled =
      count <= 0 ||
      state.outreachAcceptanceDeleteSubmitting;

    els.outreachAcceptanceDeleteSelectedButton.textContent =
      count > 0
        ? `Delete selected (${count})`
        : "Delete selected";
  }
}


function openAcceptanceDeleteJobsModal() {
  const selectedIds = Array.from(
    state.outreachAcceptanceSelectedDeleteJobIds
  );

  if (
    !selectedIds.length ||
    !els.outreachDeleteJobsModal
  ) {
    return;
  }

  const selectedJobs =
    state.outreachRecentJobs.filter(
      (job) =>
        selectedIds.includes(
          String(job.id || "").trim()
        )
    );

  const labels =
    selectedJobs
      .map(
        (job) =>
          String(
            getConnectCampaignLabel(job) ||
            job.id ||
            ""
          ).trim()
      )
      .filter(Boolean);

  if (els.outreachDeleteJobsSummary) {
    els.outreachDeleteJobsSummary.textContent =
      labels.length === 1
        ? `Delete Connect Job ${labels[0]} permanently?`
        : `Delete ${labels.length} selected Connect Jobs permanently?`;
  }

  if (els.outreachDeleteJobsError) {
    els.outreachDeleteJobsError.hidden = true;
    els.outreachDeleteJobsError.textContent = "";
  }

  els.outreachDeleteJobsModal.hidden = false;
}


function closeAcceptanceDeleteJobsModal() {
  if (state.outreachAcceptanceDeleteSubmitting) {
    return;
  }

  if (els.outreachDeleteJobsModal) {
    els.outreachDeleteJobsModal.hidden = true;
  }
}


async function deleteSelectedAcceptanceJobs() {
  const jobIds = Array.from(
    state.outreachAcceptanceSelectedDeleteJobIds
  );

  if (
    !jobIds.length ||
    state.outreachAcceptanceDeleteSubmitting
  ) {
    return;
  }

  state.outreachAcceptanceDeleteSubmitting = true;
  updateAcceptanceDeleteSelectionUi();

  if (els.outreachDeleteJobsConfirmButton) {
    els.outreachDeleteJobsConfirmButton.disabled = true;
    els.outreachDeleteJobsConfirmButton.textContent = "Deleting...";
  }

  if (els.outreachDeleteJobsError) {
    els.outreachDeleteJobsError.hidden = true;
    els.outreachDeleteJobsError.textContent = "";
  }

  try {
    for (const jobId of jobIds) {
      const response = await fetch(
        `/api/outreach/connect/jobs/${encodeURIComponent(jobId)}`,
        {
          method: "DELETE",
          headers: {
            "Accept": "application/json"
          }
        }
      );

      const result = await response.json();

      if (!response.ok || !result.ok) {
        const job =
          state.outreachRecentJobs.find(
            (item) =>
              String(item.id || "").trim() === jobId
          );

        throw new Error(
          `${getConnectCampaignLabel(job) || jobId}: ${
            result.detail ||
            result.error ||
            "Delete failed."
          }`
        );
      }

      state.outreachAcceptanceHistoryByJobId.delete(jobId);
    }

    // Remove deleted jobs from the local UI immediately.
    // Do not wait for the next dashboard poll.
    state.outreachRecentJobs =
      state.outreachRecentJobs.filter(
        (job) =>
          !jobIds.includes(
            String(
              job.id ||
              ""
            ).trim()
          )
      );

    state.outreachAcceptanceSelectedDeleteJobIds.clear();

    if (els.outreachDeleteJobsModal) {
      els.outreachDeleteJobsModal.hidden = true;
    }

    // Re-render immediately so the deleted rows disappear at once.
    if (
      state.outreachAcceptancePage > 1
      && (
        (
          state.outreachAcceptancePage - 1
        ) * OUTREACH_ACCEPTANCE_PAGE_SIZE
      ) >= state.outreachRecentJobs.length
    ) {
      state.outreachAcceptancePage -= 1;
    }

    renderOutreachAcceptanceJobs(
      state.outreachRecentJobs
    );

    // Then refresh related data from the backend in the background.
    await Promise.all([
      loadOutreachDashboard(),
      loadOutreachAcceptedPool(),
      loadMessagePreparation(),
      loadMessageBatches()
    ]);

    // Acceptance Insights is derived from Connect Job / target data.
    // Invalidate it after every successful delete.
    state.acceptanceInsights = null;
    state.acceptanceInsightsError = null;

    // If the drawer is open, refresh immediately so the table changes
    // without closing/reopening the drawer.
    if (
      els.sessionStatusModal &&
      !els.sessionStatusModal.hidden
    ) {
      closeSessionStatusModal();
      return;
    }

    if (
      els.acceptanceInsightsDrawer?.classList.contains(
        "is-open"
      )
    ) {
      await loadAcceptanceInsights();
    }

  } catch (error) {
    if (els.outreachDeleteJobsError) {
      els.outreachDeleteJobsError.hidden = false;
      els.outreachDeleteJobsError.textContent =
        error.message || String(error);
    }

  } finally {
    state.outreachAcceptanceDeleteSubmitting = false;

    if (els.outreachDeleteJobsConfirmButton) {
      els.outreachDeleteJobsConfirmButton.disabled = false;
      els.outreachDeleteJobsConfirmButton.textContent =
        "Delete permanently";
    }

    updateAcceptanceDeleteSelectionUi();
  }
}


function getWeekInfo(dateValue) {
  const date = new Date(dateValue);

  if (Number.isNaN(date.getTime())) {
    return null;
  }

  date.setHours(0, 0, 0, 0);
  const dayFromMonday = (date.getDay() + 6) % 7;
  const start = new Date(date);
  start.setDate(date.getDate() - dayFromMonday);

  const end = new Date(start);
  end.setDate(start.getDate() + 6);

  const weekNumber = getIsoWeekNumber(date);
  const isoYear = new Date(date);
  isoYear.setDate(date.getDate() + 3 - ((date.getDay() + 6) % 7));

  const dateLabel = new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric"
  });

  return {
    key: `${isoYear.getFullYear()}-W${String(weekNumber).padStart(2, "0")}`,
    weekNumber,
    year: isoYear.getFullYear(),
    start,
    end,
    label: `Week ${weekNumber} · ${dateLabel.format(start)}–${dateLabel.format(end)}`
  };
}


function getIsoWeekNumber(date) {
  const value = new Date(date);
  value.setHours(0, 0, 0, 0);
  value.setDate(value.getDate() + 3 - ((value.getDay() + 6) % 7));
  const firstThursday = new Date(value.getFullYear(), 0, 4);
  return 1 + Math.round(
    ((value - firstThursday) / 86400000 - 3 + ((firstThursday.getDay() + 6) % 7)) / 7
  );
}


function getAcceptancePeriodRows(jobs) {
  const rows = (Array.isArray(jobs) ? jobs : []).filter((job) =>
    !state.outreachAcceptanceCampaign ||
    String(job.display_name || "").trim().toLocaleLowerCase() === state.outreachAcceptanceCampaign.toLocaleLowerCase()
  );

  if (!state.outreachAcceptanceWeekKey) {
    return [];
  }

  return rows.filter((job) => {
    return getWeekInfo(job?.created_at)?.key === state.outreachAcceptanceWeekKey;
  });
}


function getAcceptanceAcceptedCount(acceptance) {
  if (!acceptance) {
    return 0;
  }

  const allRunsCount = Number(
    acceptance.all_runs_new_accepted_count
  );

  return Number.isFinite(allRunsCount)
    ? allRunsCount
    : Number(acceptance.new_accepted_count || 0);
}


function getAcceptanceWeekGroups(jobs) {
  const groups = new Map();

  (Array.isArray(jobs) ? jobs : []).filter((job) =>
    !state.outreachAcceptanceCampaign ||
    String(job.display_name || "").trim().toLocaleLowerCase() === state.outreachAcceptanceCampaign.toLocaleLowerCase()
  ).forEach((job) => {
    const info = getWeekInfo(job?.created_at);

    if (!info) {
      return;
    }

    if (!groups.has(info.key)) {
      groups.set(info.key, {
        ...info,
        jobs: [],
        totalProfiles: 0,
        accepted: 0,
        pending: 0,
        failed: 0
      });
    }

    const group = groups.get(info.key);
    const acceptance = job.acceptance || {};
    group.jobs.push(job);
    group.totalProfiles += Number(job.target_count || 0);
    group.accepted += getAcceptanceAcceptedCount(acceptance);
    group.pending += Number(acceptance.still_pending_count || 0);
    group.failed += Number(acceptance.failed_count || 0);
  });

  return Array.from(groups.values()).sort((left, right) => right.start - left.start);
}


function getAcceptanceRate(accepted, sent) {
  const acceptedCount = Number(accepted || 0);
  const sentCount = Number(sent || 0);

  if (!sentCount) {
    return "—";
  }

  return `${((acceptedCount / sentCount) * 100).toFixed(1)}%`;
}


function createEmptyAcceptanceWeekGroup(info) {
  return {
    ...info,
    jobs: [],
    totalProfiles: 0,
    accepted: 0,
    pending: 0,
    failed: 0
  };
}


function renderAcceptanceWeekOption(group, selectedKey, currentKey) {
  const rate = getAcceptanceRate(group.accepted, group.totalProfiles);
  const element = document.createElement("button");

  element.type = "button";
  element.className = "acceptance-week-option";
  element.dataset.acceptanceWeekOption = group.key;
  element.setAttribute("aria-pressed", String(group.key === selectedKey));

  element.innerHTML = `
    <span class="acceptance-week-option-copy">
      <strong>${escapeHtml(group.label)}${group.key === currentKey ? " · Current" : ""}</strong>
      <small>${group.jobs.length} ${group.jobs.length === 1 ? "job" : "jobs"} · ${group.accepted} accepted · ${rate} rate</small>
    </span>
    <span class="acceptance-week-option-check" aria-hidden="true">✓</span>
  `;

  return element;
}


function getAcceptanceWeekSelection(jobs) {
  const groups = getAcceptanceWeekGroups(jobs);
  const current = getWeekInfo(new Date());
  const requestedKey = state.outreachAcceptanceWeekKey;
  const selectedKey = groups.some((group) => group.key === requestedKey)
    ? requestedKey
    : groups[0]?.key || current?.key;
  const selectedGroup = groups.find((group) => group.key === selectedKey);

  if (state.outreachAcceptanceWeekKey !== selectedKey) {
    state.outreachAcceptanceWeekKey = selectedKey;
  }

  return {
    groups,
    current,
    selected: selectedGroup || createEmptyAcceptanceWeekGroup(current)
  };
}


function renderAcceptanceWeekList(jobs) {
  const selection = getAcceptanceWeekSelection(jobs);

  if (els.outreachAcceptanceWeekPicker) {
    els.outreachAcceptanceWeekPicker.hidden = false;
  }
  if (els.outreachAcceptanceWeekButtonLabel) {
    els.outreachAcceptanceWeekButtonLabel.textContent = selection.selected.label;
  }

  if (els.outreachAcceptanceWeekMenu) {
    const currentGroup = selection.groups.find(
      (group) => group.key === selection.current?.key
    ) || createEmptyAcceptanceWeekGroup(selection.current);
    const options = [
      currentGroup,
      ...selection.groups.filter((group) => group.key !== selection.current?.key)
    ];

    els.outreachAcceptanceWeekMenu.replaceChildren(
      ...options.map((group) => renderAcceptanceWeekOption(
        group,
        state.outreachAcceptanceWeekKey,
        selection.current?.key
      ))
    );
  }

}


function setAcceptanceWeekMenuOpen(open, {restoreFocus = false} = {}) {
  if (!els.outreachAcceptanceWeekMenu || !els.outreachAcceptanceWeekButton) {
    return;
  }

  els.outreachAcceptanceWeekMenu.hidden = !open;
  els.outreachAcceptanceWeekButton.setAttribute("aria-expanded", String(open));
  if (!open && restoreFocus) {
    els.outreachAcceptanceWeekButton.focus();
  }
}


function renderAcceptancePeriodFilters() {
  const select = els.outreachAcceptanceCampaignFilter;
  if (select) {
    const namesByKey = new Map();
    for (const job of state.outreachRecentJobs) {
      const name = String(job.display_name || "").trim();
      if (name) namesByKey.set(name.toLocaleLowerCase(), namesByKey.get(name.toLocaleLowerCase()) || name);
    }
    const names = [...namesByKey.values()].sort((a, b) => a.localeCompare(b));
    const selectedKey = state.outreachAcceptanceCampaign.toLocaleLowerCase();
    state.outreachAcceptanceCampaign = namesByKey.get(selectedKey) || "";
    const currentNames = [...select.options].slice(1).map((option) => option.value);
    if (names.join("\u0000") !== currentNames.join("\u0000")) {
      const selected = state.outreachAcceptanceCampaign;
      select.replaceChildren(new Option("All campaigns", ""));
      for (const name of names) select.add(new Option(name, name));
      if (namesByKey.has(selected.toLocaleLowerCase())) {
        select.value = selected;
      } else {
        state.outreachAcceptanceCampaign = "";
        select.value = "";
      }
    } else {
      select.value = state.outreachAcceptanceCampaign;
    }
  }
  renderConnectDropdown(connectDropdowns[2]);
  renderAcceptanceWeekList(state.outreachRecentJobs);

}

function renderAcceptanceCampaignSummary(rows) {
  const visible = Boolean(state.outreachAcceptanceCampaign) && rows.length > 0;
  const summary = els.outreachAcceptanceCampaignSummary;
  if (!summary) return;
  summary.hidden = !visible;
  if (!visible) return;

  const totals = rows.reduce((result, job) => {
    const acceptance = job.acceptance || {};
    result.prospects += Number(job.input_count || 0);
    result.accepted += getAcceptanceAcceptedCount(acceptance);
    result.pending += Number(acceptance.still_pending_count || 0);
    result.failed += Number(acceptance.failed_count || 0);
    return result;
  }, { prospects: 0, accepted: 0, pending: 0, failed: 0 });
  const setText = (element, text) => { if (element) element.textContent = String(text); };
  setText(els.outreachAcceptanceCampaignSummaryName, state.outreachAcceptanceCampaign);
  setText(els.outreachAcceptanceCampaignSummaryBatches, `${rows.length} ${rows.length === 1 ? "batch" : "batches"}`);
  setText(els.outreachAcceptanceCampaignSummaryProspects, totals.prospects);
  setText(els.outreachAcceptanceCampaignSummaryAccepted, totals.accepted);
  setText(els.outreachAcceptanceCampaignSummaryPending, totals.pending);
  setText(els.outreachAcceptanceCampaignSummaryFailed, totals.failed);
}


function renderOutreachAcceptanceJobs(
  jobs
) {
  renderAcceptancePeriodFilters();

  const rows = getAcceptancePeriodRows(jobs);
  renderAcceptanceCampaignSummary(rows);
  updateAcceptanceDeleteSelectionUi();

  if (
    !els.outreachAcceptanceEmpty ||
    !els.outreachAcceptanceTableWrap ||
    !els.outreachAcceptanceBody ||
    !els.outreachAcceptanceRowTemplate
  ) {
    return;
  }

  if (!rows.length) {
    els.outreachAcceptanceEmpty.hidden = false;
    els.outreachAcceptanceEmpty.textContent = "No Connect Jobs in this week.";
    els.outreachAcceptanceTableWrap.hidden = true;
    els.outreachAcceptanceBody.replaceChildren();

    if (els.outreachAcceptancePagination) {
      els.outreachAcceptancePagination.hidden = true;
    }

    return;
  }

  const pageSize = Number(
    state.outreachAcceptancePageSize || 10
  );

  const totalPages = Math.max(
    1,
    Math.ceil(rows.length / pageSize)
  );

  state.outreachAcceptancePage =
    Math.min(
      totalPages,
      Math.max(
        1,
        state.outreachAcceptancePage
      )
    );

  const startIndex =
    (state.outreachAcceptancePage - 1) *
    pageSize;

  const pageRows =
    rows.slice(
      startIndex,
      startIndex + pageSize
    );

  els.outreachAcceptanceEmpty.hidden = true;
  els.outreachAcceptanceTableWrap.hidden = false;
  els.outreachAcceptanceBody.replaceChildren();
  els.outreachAcceptanceTableWrap.classList.remove("is-page-entering");
  void els.outreachAcceptanceTableWrap.offsetWidth;
  els.outreachAcceptanceTableWrap.classList.add("is-page-entering");
  window.setTimeout(() => {
    els.outreachAcceptanceTableWrap?.classList.remove("is-page-entering");
  }, 240);

  pageRows.forEach((job) => {
    const acceptance =
      job.acceptance || null;

    const acceptanceStatus =
      getAcceptanceDisplayStatus(
        acceptance
      );

    const connectStatus =
      normaliseStatus(
        job.status
      );

    const fragment =
      els.outreachAcceptanceRowTemplate
        .content
        .cloneNode(true);

    const setText = (
      selector,
      value
    ) => {
      const element =
        fragment.querySelector(
          selector
        );

      if (element) {
        element.textContent =
          String(value);
      }
    };

    setText(
      "[data-acceptance-job-code]",
      getConnectCampaignLabel(job) || "—"
    );

    setText(
      "[data-acceptance-created]",
      formatDate(job.created_at)
    );

    setText(
      "[data-acceptance-profile-count]",
      Number(job.target_count || 0)
    );

    const outcomeCounts = {
      accepted: acceptance ? Math.max(0, Number(getAcceptanceAcceptedCount(acceptance)) || 0) : 0,
      pending: acceptance ? Math.max(0, Number(acceptance.still_pending_count) || 0) : 0,
      unknown: acceptance ? Math.max(0, Number(acceptance.declined_or_unknown_count) || 0) : 0,
      failed: acceptance ? Math.max(0, Number(acceptance.failed_count) || 0) : 0
    };

    setText("[data-acceptance-accepted]", acceptance ? outcomeCounts.accepted : "—");

    const outcomesTrack = fragment.querySelector(".acceptance-outcomes-track");
    if (outcomesTrack) {
      const measuredTotal = Object.values(outcomeCounts).reduce((sum, value) => sum + value, 0);
      const denominator = Math.max(1, Number(job.target_count || 0), measuredTotal);
      Object.entries(outcomeCounts).forEach(([status, count]) => {
        const bar = fragment.querySelector(`[data-acceptance-${status}-bar]`);
        if (bar) {
          bar.style.width = `${Math.min(100, (count / denominator) * 100)}%`;
        }
      });
      outcomesTrack.setAttribute(
        "aria-label",
        acceptance
          ? `Accepted ${outcomeCounts.accepted}, pending ${outcomeCounts.pending}, unknown ${outcomeCounts.unknown}, failed ${outcomeCounts.failed}`
          : "Not checked"
      );

      Object.entries(outcomeCounts).forEach(([status, count]) => {
        const tag = fragment.querySelector(`[data-acceptance-${status}-tag]`);
        if (tag) {
          tag.textContent = `${status[0].toUpperCase()}${status.slice(1)} ${count}`;
        }
      });
    }

    const lastCheckedAt =
      getLatestAcceptanceCheckedAt(
        acceptance
      );

    setText(
      "[data-acceptance-last-checked]",
      lastCheckedAt
        ? formatDate(lastCheckedAt)
        : "Never"
    );

    const connectStatusElement =
      fragment.querySelector(
        "[data-acceptance-connect-status]"
      );

    if (connectStatusElement) {
      connectStatusElement.textContent =
        statusLabel(connectStatus);

      connectStatusElement.className =
        `pill ${getOutreachPillClass(
          connectStatus
        )}`;
    }

    const acceptanceStatusElement =
      fragment.querySelector(
        "[data-acceptance-status]"
      );

    if (acceptanceStatusElement) {
      acceptanceStatusElement.textContent =
        getAcceptanceStatusLabel(
          acceptance
        );

      acceptanceStatusElement.className =
        `pill ${getOutreachPillClass(
          acceptanceStatus
        )}`;
    }

    const deleteCheckbox =
      fragment.querySelector(
        "[data-acceptance-delete-select]"
      );

    if (deleteCheckbox) {
      const deleteJobId =
        String(job.id || "").trim();

      deleteCheckbox.checked =
        state.outreachAcceptanceSelectedDeleteJobIds.has(
          deleteJobId
        );

      const acceptanceStatus =
        normaliseStatus(
          job.acceptance?.status ||
          ""
        );

      const jobStatus =
        normaliseStatus(
          job.status ||
          ""
        );

      deleteCheckbox.disabled =
        state.outreachAcceptanceDeleteSubmitting ||
        [
          "pending",
          "running",
          "processing",
          "starting"
        ].includes(jobStatus) ||
        [
          "pending",
          "running"
        ].includes(acceptanceStatus);

      deleteCheckbox.addEventListener(
        "change",
        () => {
          if (deleteCheckbox.checked) {
            state.outreachAcceptanceSelectedDeleteJobIds.add(
              deleteJobId
            );
          } else {
            state.outreachAcceptanceSelectedDeleteJobIds.delete(
              deleteJobId
            );
          }

          updateAcceptanceDeleteSelectionUi();
        }
      );
    }

    const historyButton =
      fragment.querySelector(
        "[data-acceptance-history-button]"
      );

    if (historyButton) {
      const historyJobId =
        String(
          job.id ||
          ""
        ).trim();

      historyButton.dataset.jobId =
        historyJobId;

      historyButton.setAttribute(
        "aria-expanded",
        "false"
      );

      historyButton.textContent = "History";

      historyButton.addEventListener(
        "click",
        async () => {
          openAcceptanceHistoryModal(job);
        }
      );
    }

    const button =
      fragment.querySelector(
        "[data-acceptance-check-button]"
      );

    if (button) {
      const jobId =
        String(job.id || "").trim();

      const submitting =
        state
          .outreachAcceptanceSubmittingJobIds
          .has(jobId);

      const busy =
        acceptanceStatus === "pending" ||
        acceptanceStatus === "running";

      const canCheck =
        Boolean(jobId) &&
        connectStatus === "completed" &&
        !busy &&
        !submitting;

      button.dataset.jobId = jobId;
      button.disabled = !canCheck;

      button.textContent =
        submitting
          ? "Queueing..."
          : acceptanceStatus === "pending"
            ? "Queued"
            : acceptanceStatus === "running"
              ? "Checking..."
              : "Check again";

      button.addEventListener(
        "click",
        async () => {
          try {
            await queueOutreachAcceptanceCheck(
              jobId
            );
          } catch (error) {
            console.error(
              "Acceptance check error:",
              error
            );
          }
        }
      );
    }

    els.outreachAcceptanceBody.append(
      fragment
    );

  });

  updateSimplePagination({
    container:
      els.outreachAcceptancePagination,
    meta:
      els.outreachAcceptancePageMeta,
    prev:
      els.outreachAcceptancePrevPage,
    next:
      els.outreachAcceptanceNextPage,
    currentPage:
      state.outreachAcceptancePage,
    totalPages,
    totalItems:
      rows.length,
    startIndex,
    pageLength:
      pageRows.length
  });
}


// ---------------------------------------------------------
// ACCEPTED POOL
// ---------------------------------------------------------


function ensureOutreachAcceptedPoolPanel() {
  return (
    els.outreachAcceptedPoolPanel ||
    document.querySelector("#outreachAcceptedPoolPanel")
  );
}


function getEligibleMessageProspectIds() {
  const items =
    Array.isArray(
      state.messagePreparation?.items
    )
      ? state.messagePreparation.items
      : [];

  return new Set(
    items
      .map(
        (item) =>
          String(
            item.prospect_id || ""
          ).trim()
      )
      .filter(Boolean)
  );
}


function getAcceptedPoolVisibleItems() {
  const items = Array.isArray(state.outreachAcceptedPool?.items)
    ? state.outreachAcceptedPool.items
    : [];

  if (!state.outreachAcceptedPoolWeekKey) {
    return [];
  }

  return items.filter((item) => {
    const info = getWeekInfo(item?.job_created_at);
    return info?.key === state.outreachAcceptedPoolWeekKey;
  });
}

function acceptedPoolCampaignKey(item) {
  return String(item?.campaign_id || "").trim() ||
    `batch:${String(item?.connect_batch_id || item?.job_id || "unknown").trim()}`;
}

function acceptedPoolCampaignName(item) {
  let name = String(item?.campaign_name || item?.display_name || "").trim();
  while (name) {
    const canonical = name
      .replace(/^(?:\d{1,2}\/\d{1,2}\/\d{4}|\d{4}-\d{2}-\d{2})\s*[-–—:]\s*/, "")
      .replace(/^(?:lần|lan)\s*\d+\s*[-–—:]\s*/i, "")
      .trim();
    if (!canonical || canonical === name) break;
    name = canonical;
  }
  return name || "Campaign unavailable";
}

function renderAcceptedPoolCampaignFilter() {
  const menu = els.outreachAcceptedCampaignMenu;
  if (!menu) return;
  const campaigns = new Map();
  for (const item of getAcceptedPoolVisibleItems()) {
    const id = acceptedPoolCampaignKey(item);
    const existing = campaigns.get(id);
    campaigns.set(id, {
      name: acceptedPoolCampaignName(item),
      count: (existing?.count || 0) + 1
    });
  }
  const items = getAcceptedPoolVisibleItems();
  const options = [
    ["", { name: "All campaigns", count: items.length }],
    ...[...campaigns.entries()].sort((left, right) =>
      left[1].name.localeCompare(right[1].name, undefined, { sensitivity: "base" }))
  ];
  if (!campaigns.has(state.outreachAcceptedCampaignId)) {
    state.outreachAcceptedCampaignId = "";
  }
  const selected = campaigns.get(state.outreachAcceptedCampaignId);
  if (els.outreachAcceptedCampaignButtonLabel) {
    els.outreachAcceptedCampaignButtonLabel.textContent = selected?.name || "All campaigns";
  }
  if (els.outreachAcceptedCampaignButton) {
    els.outreachAcceptedCampaignButton.setAttribute("aria-expanded", String(!menu.hidden));
  }
  menu.replaceChildren(...options.map(([id, campaign]) => {
    const option = document.createElement("button");
    option.type = "button";
    option.className = "recipient-week-option";
    option.dataset.acceptedCampaignOption = id;
    option.setAttribute("aria-pressed", String(id === state.outreachAcceptedCampaignId));
    option.innerHTML = "<span class=\"recipient-week-option-copy\"><strong>" +
      escapeHtml(campaign.name) + "</strong><small>" + campaign.count + " " +
      (campaign.count === 1 ? "recipient" : "recipients") +
      "</small></span><span class=\"recipient-week-option-check\" aria-hidden=\"true\">✓</span>";
    return option;
  }));
}

function getAcceptedPoolCampaignItems() {
  const items = getAcceptedPoolVisibleItems();
  const campaignId = state.outreachAcceptedCampaignId;
  return campaignId
    ? items.filter((item) => acceptedPoolCampaignKey(item) === campaignId)
    : items;
}


function getAcceptedPoolWeekGroups() {
  const groups = new Map();
  const eligibleIds = getEligibleMessageProspectIds();

  (Array.isArray(state.outreachRecentJobs) ? state.outreachRecentJobs : [])
    .forEach((job) => {
      const info = getWeekInfo(job?.created_at);
      if (!info) return;
      if (!groups.has(info.key)) {
        groups.set(info.key, {
          ...info, profiles: 0, ready: 0, prepared: 0,
          sent: 0, jobCount: 0, batches: new Set()
        });
      }
      groups.get(info.key).jobCount += 1;
    });

  (Array.isArray(state.outreachAcceptedPool?.items)
    ? state.outreachAcceptedPool.items
    : []
  ).forEach((item) => {
    const info = getWeekInfo(item?.job_created_at);

    if (!info) {
      return;
    }

    if (!groups.has(info.key)) {
      groups.set(info.key, {
        ...info,
        profiles: 0,
        ready: 0,
        prepared: 0,
        sent: 0,
        jobCount: 0,
        batches: new Set()
      });
    }

    const group = groups.get(info.key);
    const bucket = getAcceptedPoolUiBucket(item, eligibleIds);
    group.profiles += 1;
    group[bucket] = Number(group[bucket] || 0) + 1;

    const batchCode = getAcceptedPoolBatchCode(item);
    if (batchCode) {
      group.batches.add(batchCode);
    }
  });

  return Array.from(groups.values())
    .map((group) => ({ ...group, batchCount: group.batches.size }))
    .sort((left, right) => right.start - left.start);
}


function createEmptyAcceptedPoolWeekGroup(weekInfo) {
  return {
    ...(weekInfo || {
      key: "current",
      label: "Current week",
      start: Date.now()
    }),
    profiles: 0,
    ready: 0,
    prepared: 0,
    sent: 0,
    jobCount: 0,
    batches: new Set(),
    batchCount: 0
  };
}


function renderAcceptedPoolWeekOption(group, selectedKey, currentKey) {
  const element = document.createElement("button");
  element.type = "button";
  element.className = "recipient-week-option";
  element.dataset.acceptedWeekOption = group.key;
  element.setAttribute("aria-pressed", String(group.key === selectedKey));
  element.innerHTML = `
    <span class="recipient-week-option-copy">
      <strong>${escapeHtml(group.label)}${group.key === currentKey ? " · Current" : ""}</strong>
      <small>${group.jobCount} Connect ${group.jobCount === 1 ? "job" : "jobs"} · ${group.profiles} accepted profiles</small>
    </span>
    <span class="recipient-week-option-check" aria-hidden="true">✓</span>
  `;
  return element;
}


function getAcceptedPoolWeekSelection() {
  const groups = getAcceptedPoolWeekGroups();
  const current = getWeekInfo(new Date());
  const requestedKey = state.outreachAcceptedPoolWeekKey || current?.key;
  const selectedKey = requestedKey === current?.key || groups.some(
    (group) => group.key === requestedKey
  ) ? requestedKey : current?.key;
  const selectedGroup = groups.find((group) => group.key === selectedKey);

  if (state.outreachAcceptedPoolWeekKey !== selectedKey) {
    state.outreachAcceptedPoolWeekKey = selectedKey;
  }

  return {
    groups,
    current,
    selected: selectedGroup || createEmptyAcceptedPoolWeekGroup(
      selectedKey === current?.key
        ? current
        : getWeekInfo(new Date(selectedGroup?.start || current?.start || Date.now()))
    )
  };
}


function renderAcceptedPoolWeekList() {
  const selection = getAcceptedPoolWeekSelection();
  if (els.outreachAcceptedWeekButtonLabel) {
    els.outreachAcceptedWeekButtonLabel.textContent = selection.selected.label;
  }
  if (els.outreachAcceptedWeekMenu) {
    const currentGroup = selection.groups.find(
      (group) => group.key === selection.current?.key
    ) || createEmptyAcceptedPoolWeekGroup(selection.current);
    const options = [
      currentGroup,
      ...selection.groups.filter((group) => group.key !== selection.current?.key)
    ];
    els.outreachAcceptedWeekMenu.replaceChildren(
      ...options.map((group) => renderAcceptedPoolWeekOption(
        group, selection.selected.key, selection.current?.key
      ))
    );
  }
}


function setAcceptedPoolWeekMenuOpen(open, {restoreFocus = false} = {}) {
  if (!els.outreachAcceptedWeekMenu || !els.outreachAcceptedWeekButton) {
    return;
  }
  els.outreachAcceptedWeekMenu.hidden = !open;
  els.outreachAcceptedWeekButton.setAttribute("aria-expanded", String(open));
  if (!open && restoreFocus) {
    els.outreachAcceptedWeekButton.focus();
  }
}

function setAcceptedPoolCampaignMenuOpen(open, {restoreFocus = false} = {}) {
  if (!els.outreachAcceptedCampaignMenu || !els.outreachAcceptedCampaignButton) {
    return;
  }
  els.outreachAcceptedCampaignMenu.hidden = !open;
  els.outreachAcceptedCampaignButton.setAttribute("aria-expanded", String(open));
  if (!open && restoreFocus) els.outreachAcceptedCampaignButton.focus();
}


function getAcceptedPoolBatchCode(
  item
) {
  return String(
    item?.job_id ||
    ""
  ).trim();
}


function getAcceptedPoolConnectIdLabel(
  item
) {
  if (item?.batch_label) return String(item.batch_label);
  const jobCode =
    String(
      item?.job_code ||
      ""
    ).trim();

  if (jobCode) {
    return jobCode;
  }

  const jobId =
    getAcceptedPoolBatchCode(
      item
    );

  if (!jobId) {
    return "Unknown Connect ID";
  }

  return jobId.length > 16
    ? `${jobId.slice(0, 8)}…${jobId.slice(-5)}`
    : jobId;
}


function sortAcceptedPoolBySendBatch(
  items
) {
  return [
    ...items
  ].sort(
    (left, right) => {
      const campaignOrder = acceptedPoolCampaignName(left).localeCompare(
        acceptedPoolCampaignName(right), undefined, { sensitivity: "base" }
      );
      if (campaignOrder) return campaignOrder;
      const campaignIdOrder = acceptedPoolCampaignKey(left).localeCompare(
        acceptedPoolCampaignKey(right)
      );
      if (campaignIdOrder) return campaignIdOrder;
      const leftBatch =
        getAcceptedPoolBatchCode(
          left
        );

      const rightBatch =
        getAcceptedPoolBatchCode(
          right
        );

      // Ready / unassigned stays as its own group after assigned batches.
      if (
        Boolean(leftBatch) !==
        Boolean(rightBatch)
      ) {
        return leftBatch
          ? -1
          : 1;
      }

      if (
        leftBatch !==
        rightBatch
      ) {
        const leftLabel =
          getAcceptedPoolConnectIdLabel(
            left
          );

        const rightLabel =
          getAcceptedPoolConnectIdLabel(
            right
          );

        return rightLabel.localeCompare(
          leftLabel,
          undefined,
          {
            numeric: true,
            sensitivity: "base"
          }
        );
      }

      const leftAccount =
        String(
          left?.assigned_account_id ||
          ""
        );

      const rightAccount =
        String(
          right?.assigned_account_id ||
          ""
        );

      return leftAccount.localeCompare(
        rightAccount,
        undefined,
        {
          sensitivity: "base"
        }
      );
    }
  );
}



function getAcceptedPoolUiBucket(
  item,
  eligibleIds = null
) {
  const messageBucket =
    String(
      item?.message_bucket ||
      "not_sent"
    ).toLowerCase();

  if (messageBucket === "sent") {
    return "sent";
  }

  const prospectId =
    String(
      item?.prospect_id ||
      ""
    ).trim();

  const readyIds =
    eligibleIds ||
    getEligibleMessageProspectIds();

  if (
    prospectId &&
    readyIds.has(prospectId)
  ) {
    return "ready";
  }

  return "prepared";
}


function getAcceptedPoolFilteredItems() {
  const items = getAcceptedPoolCampaignItems();

  const filter =
    state.outreachAcceptedPoolFilter ||
    "all";

  const eligibleIds =
    getEligibleMessageProspectIds();

  const filtered =
    items.filter((item) => {
    const statusMatches =
      filter === "all" ||
      getAcceptedPoolUiBucket(
        item,
        eligibleIds
      ) === filter;

    return statusMatches;
  });

  return sortAcceptedPoolBySendBatch(
    filtered
  );
}

function getAcceptedPoolUiSummary() {
  const items = getAcceptedPoolCampaignItems();

  const eligibleIds =
    getEligibleMessageProspectIds();

  const summary = {
    all: items.length,
    ready: 0,
    prepared: 0,
    sent: 0
  };

  items.forEach((item) => {
    const bucket =
      getAcceptedPoolUiBucket(
        item,
        eligibleIds
      );

    if (
      Object.prototype.hasOwnProperty.call(
        summary,
        bucket
      )
    ) {
      summary[bucket] += 1;
    }
  });

  return summary;
}


function reconcileAcceptedPoolSelection() {
  const eligibleIds =
    getEligibleMessageProspectIds();

  for (
    const prospectId of Array.from(
      state.outreachAcceptedSelectedProspectIds
    )
  ) {
    if (!eligibleIds.has(prospectId)) {
      state
        .outreachAcceptedSelectedProspectIds
        .delete(prospectId);
    }
  }
}


function getAcceptedPoolPageData() {
  const filteredItems =
    getAcceptedPoolFilteredItems();

  const pageSize = 15;

  const totalPages = Math.max(
    1,
    Math.ceil(
      filteredItems.length /
      pageSize
    )
  );

  const currentPage = Math.min(
    totalPages,
    Math.max(
      1,
      Number(
        state.outreachAcceptedPoolPage ||
        1
      )
    )
  );

  state.outreachAcceptedPoolPage =
    currentPage;

  const startIndex =
    (
      currentPage -
      1
    ) *
    pageSize;

  return {
    filteredItems,
    pageItems:
      filteredItems.slice(
        startIndex,
        startIndex + pageSize
      ),
    currentPage,
    totalPages,
    startIndex
  };
}


function renderAcceptedPoolPagination(
  pageData
) {
  if (!els.outreachAcceptedPagination) {
    return;
  }

  const {
    filteredItems,
    pageItems,
    currentPage,
    totalPages,
    startIndex
  } = pageData;

  els.outreachAcceptedPagination.hidden =
    filteredItems.length === 0;

  if (!filteredItems.length) {
    return;
  }

  if (els.outreachAcceptedPageMeta) {
    els.outreachAcceptedPageMeta.textContent =
      `Page ${currentPage} / ${totalPages} · ${startIndex + 1}-${startIndex + pageItems.length} of ${filteredItems.length}`;
  }

  if (els.outreachAcceptedPrevPage) {
    els.outreachAcceptedPrevPage.disabled =
      currentPage <= 1;
  }

  if (els.outreachAcceptedNextPage) {
    els.outreachAcceptedNextPage.disabled =
      currentPage >= totalPages;
  }
}


function updateAcceptedPoolPageSelectControl(
  pageItems
) {
  const control =
    els.outreachAcceptedSelectPage;

  if (!control) {
    return;
  }

  const eligibleIds =
    getEligibleMessageProspectIds();

  const selectableIds =
    pageItems
      .map(
        (item) =>
          String(
            item.prospect_id || ""
          ).trim()
      )
      .filter(
        (id) =>
          Boolean(id) &&
          eligibleIds.has(id)
      );

  const selectedCount =
    selectableIds.filter(
      (id) =>
        state
          .outreachAcceptedSelectedProspectIds
          .has(id)
    ).length;

  control.disabled =
    selectableIds.length === 0;

  control.checked =
    selectableIds.length > 0 &&
    selectedCount ===
      selectableIds.length;

  control.indeterminate =
    selectedCount > 0 &&
    selectedCount <
      selectableIds.length;
}


function renderOutreachAcceptedPool() {
  const panel =
    ensureOutreachAcceptedPoolPanel();

  if (!panel) {
    return;
  }

  reconcileAcceptedPoolSelection();

  renderAcceptedPoolWeekList();
  renderAcceptedPoolCampaignFilter();

  const uiSummary =
    getAcceptedPoolUiSummary();

  const pageData =
    getAcceptedPoolPageData();

  const filteredItems =
    pageData.filteredItems;

  const pageItems =
    pageData.pageItems;

  if (els.outreachAcceptedPoolSummary) {
    const selectedWeek = getAcceptedPoolWeekSelection().selected;
    const periodLabel = selectedWeek?.label || "Current week";

    const campaignLabel = state.outreachAcceptedCampaignId
      ? " · " + (els.outreachAcceptedCampaignButtonLabel?.textContent || "Campaign")
      : "";
    els.outreachAcceptedPoolSummary.textContent =
      periodLabel + campaignLabel + " · " + uiSummary.all + " accepted profiles · " +
      uiSummary.ready + " ready · " + uiSummary.prepared + " prepared · " +
      uiSummary.sent + " sent";
  }

  if (els.outreachAcceptedSelectedCount) {
    const selectedCount =
      state
        .outreachAcceptedSelectedProspectIds
        .size;

    els.outreachAcceptedSelectedCount.textContent =
      `${selectedCount} selected`;

    els.outreachAcceptedSelectedCount.className =
      `pill ${
        selectedCount > 0
          ? "pill-purple"
          : "pill-neutral"
      }`;
  }

  panel
    .querySelectorAll(
      "[data-accepted-filter]"
    )
    .forEach((button) => {
      const filter =
        button.dataset.acceptedFilter ||
        "all";

      const count =
        Number(
          uiSummary[filter] ||
          0
        );

      const label =
        filter === "ready"
          ? "Ready"
          : filter === "prepared"
            ? "Prepared"
            : filter === "sent"
              ? "Sent"
              : "All";

      button.textContent =
        `${label} ${count}`;

      button.classList.toggle(
        "is-active",
        filter ===
          state.outreachAcceptedPoolFilter
      );
    });

  if (!filteredItems.length) {
    if (els.outreachAcceptedPoolEmpty) {
      els.outreachAcceptedPoolEmpty.hidden =
        false;

      els.outreachAcceptedPoolEmpty.textContent =
        uiSummary.all > 0
          ? "No recipients match this filter."
          : "No accepted profiles found.";
    }

    if (els.outreachAcceptedPoolTableWrap) {
      els.outreachAcceptedPoolTableWrap.hidden =
        true;
    }

    els.outreachAcceptedPoolBody
      ?.replaceChildren();

    if (els.outreachAcceptedPagination) {
      els.outreachAcceptedPagination.hidden =
        true;
    }

    updateAcceptedPoolPageSelectControl(
      []
    );

    renderMessagePreparation();

    return;
  }

  if (els.outreachAcceptedPoolEmpty) {
    els.outreachAcceptedPoolEmpty.hidden =
      true;
  }

  if (els.outreachAcceptedPoolTableWrap) {
    els.outreachAcceptedPoolTableWrap.hidden =
      false;
  }

  renderAcceptedPoolPagination(
    pageData
  );

  if (
    !els.outreachAcceptedPoolBody ||
    !els.outreachAcceptedPoolRowTemplate
  ) {
    return;
  }

  const eligibleIds =
    getEligibleMessageProspectIds();

  const campaignGroups = new Map();
  for (const item of filteredItems) {
    const key = acceptedPoolCampaignKey(item);
    if (!campaignGroups.has(key)) {
      campaignGroups.set(key, { count: 0, readyIds: new Set() });
    }
    const group = campaignGroups.get(key);
    group.count += 1;
    const prospectId = String(item.prospect_id || "").trim();
    if (prospectId && eligibleIds.has(prospectId)) group.readyIds.add(prospectId);
  }

  els.outreachAcceptedPoolBody
    .replaceChildren();

  const pageBatchCounts =
    pageItems.reduce(
      (counts, item) => {
        const batchCode =
          getAcceptedPoolBatchCode(
            item
          ) || "unassigned";

        counts.set(
          batchCode,
          (
            counts.get(
              batchCode
            ) || 0
          ) + 1
        );

        return counts;
      },
      new Map()
    );

  let previousCampaignKey = null;
  let previousBatchCode = null;

  pageItems.forEach((item) => {
    const campaignKey = acceptedPoolCampaignKey(item);
    if (campaignKey !== previousCampaignKey && els.outreachAcceptedPoolCampaignTemplate) {
      const campaignFragment = els.outreachAcceptedPoolCampaignTemplate.content.cloneNode(true);
      const name = campaignFragment.querySelector("[data-recipient-campaign-name]");
      const count = campaignFragment.querySelector("[data-recipient-campaign-count]");
      const selectAll = campaignFragment.querySelector("[data-recipient-campaign-select]");
      const group = campaignGroups.get(campaignKey);
      const readyIds = [...(group?.readyIds || [])];
      const allSelected = readyIds.length > 0 && readyIds.every((id) =>
        state.outreachAcceptedSelectedProspectIds.has(id));
      if (name) name.textContent = acceptedPoolCampaignName(item);
      if (count) count.textContent = `${group?.count || 0} recipients · ${readyIds.length} ready`;
      if (selectAll) {
        selectAll.disabled = !readyIds.length || state.messagePreparationSubmitting ||
          state.messagePreparationSelectedSubmitting;
        selectAll.textContent = allSelected
          ? `Clear selected (${readyIds.length})` : `Select all ready (${readyIds.length})`;
        selectAll.setAttribute("aria-label", `${selectAll.textContent} in ${acceptedPoolCampaignName(item)}`);
        selectAll.addEventListener("click", () => {
          for (const id of readyIds) {
            if (allSelected) state.outreachAcceptedSelectedProspectIds.delete(id);
            else state.outreachAcceptedSelectedProspectIds.add(id);
          }
          renderOutreachAcceptedPool();
        });
      }
      els.outreachAcceptedPoolBody.append(campaignFragment);
      previousCampaignKey = campaignKey;
      previousBatchCode = null;
    }
    const currentBatchCode =
      getAcceptedPoolBatchCode(
        item
      ) || "unassigned";

    if (
      currentBatchCode !==
      previousBatchCode &&
      els.outreachAcceptedPoolGroupTemplate
    ) {
      const groupFragment =
        els.outreachAcceptedPoolGroupTemplate
          .content
          .cloneNode(true);

      const groupCode =
        groupFragment.querySelector(
          "[data-accepted-group-code]"
        );

      const groupCount =
        groupFragment.querySelector(
          "[data-accepted-group-count]"
        );

      if (groupCode) {
        groupCode.textContent =
          currentBatchCode ===
            "unassigned"
            ? "Unknown Connect ID"
            : getAcceptedPoolConnectIdLabel(
                item
              );

        groupCode.title =
          currentBatchCode ===
            "unassigned"
            ? ""
            : `Connect Job ID: ${currentBatchCode}`;
      }

      if (groupCount) {
        const count =
          Number(
            pageBatchCounts.get(
              currentBatchCode
            ) || 0
          );

        groupCount.textContent =
          `${count} ${
            count === 1
              ? "profile"
              : "profiles"
          }`;
      }

      els.outreachAcceptedPoolBody.append(
        groupFragment
      );

      previousBatchCode =
        currentBatchCode;
    }

    const prospectId =
      String(
        item.prospect_id ||
        ""
      ).trim();

    const linkedinUrl =
      String(
        item.linkedin_url ||
        ""
      ).trim();

    const uiBucket =
      getAcceptedPoolUiBucket(
        item,
        eligibleIds
      );

    const canSelect =
      uiBucket === "ready" &&
      Boolean(prospectId);

    const isSelected =
      canSelect &&
      state
        .outreachAcceptedSelectedProspectIds
        .has(prospectId);

    const fragment =
      els.outreachAcceptedPoolRowTemplate
        .content
        .cloneNode(true);

    const row =
      fragment.querySelector("tr");

    const checkbox =
      fragment.querySelector(
        "[data-accepted-select]"
      );

    const link =
      fragment.querySelector(
        "[data-accepted-link]"
      );

    const account =
      fragment.querySelector(
        "[data-accepted-account]"
      );

    const acceptedAt =
      fragment.querySelector(
        "[data-accepted-at]"
      );

    const sendBatch =
      fragment.querySelector(
        "[data-accepted-send-batch]"
      );

    const message =
      fragment.querySelector(
        "[data-accepted-message]"
      );

    row?.classList.toggle(
      "is-selected",
      isSelected
    );

    if (checkbox) {
      checkbox.disabled =
        !canSelect;

      checkbox.checked =
        isSelected;

      checkbox.title =
        uiBucket === "prepared"
          ? "Recipient is already in a prepared message batch."
          : uiBucket === "sent"
            ? "Message already sent."
            : "Select recipient for a new message batch.";

      checkbox.addEventListener(
        "change",
        () => {
          if (!canSelect) {
            return;
          }

          if (checkbox.checked) {
            state
              .outreachAcceptedSelectedProspectIds
              .add(prospectId);
          } else {
            state
              .outreachAcceptedSelectedProspectIds
              .delete(prospectId);
          }

          renderOutreachAcceptedPool();
        }
      );
    }

    if (link) {
      link.href =
        linkedinUrl ||
        "#";

      link.textContent =
        linkedinUrl ||
        "—";
    }

    if (account) {
      account.textContent =
        getOutreachAccountDisplayName(
          item.assigned_account_id
        );
    }

    if (acceptedAt) {
      acceptedAt.textContent =
        formatDate(
          item.accepted_at ||
          item.acceptance_checked_at
        );
    }

    if (sendBatch) {
      const jobId =
        getAcceptedPoolBatchCode(
          item
        );

      sendBatch.textContent =
        jobId
          ? getAcceptedPoolConnectIdLabel(
              item
            )
          : "—";

      sendBatch.classList.toggle(
        "is-assigned",
        Boolean(jobId)
      );

      sendBatch.title =
        jobId
          ? `Connect Job ID: ${jobId}`
          : "Connect Job ID unavailable.";
    }

    if (message) {
      const messageLabel =
        uiBucket === "sent"
          ? "Sent"
          : uiBucket === "prepared"
            ? "Prepared"
            : "Ready";

      message.textContent =
        messageLabel;

      message.className =
        `pill ${
          uiBucket === "sent"
            ? "pill-green"
            : uiBucket === "ready"
              ? "pill-purple"
              : "pill-neutral"
        }`;
    }

    els.outreachAcceptedPoolBody.append(
      fragment
    );
  });

  updateAcceptedPoolPageSelectControl(
    pageItems
  );

  renderMessagePreparation();
}


async function loadOutreachAcceptedPool() {
  try {
    const response = await fetch(
      "/api/outreach/accepted-pool",
      {
        method: "GET",
        headers: {
          "Accept": "application/json"
        },
        cache: "no-store"
      }
    );

    const result =
      await response.json();

    if (
      !response.ok ||
      !result.ok
    ) {
      throw new Error(
        result.detail ||
        result.error ||
        "Could not load the Accepted Pool."
      );
    }

    const pool =
      result.accepted_pool || {};

    state.outreachAcceptedPool = {
      summary: {
        total: Number(
          pool.summary?.total || 0
        ),
        not_sent: Number(
          pool.summary?.not_sent || 0
        ),
        sent: Number(
          pool.summary?.sent || 0
        )
      },
      items: Array.isArray(
        pool.items
      )
        ? pool.items
        : []
    };

  } catch (error) {
    console.error(
      "Accepted Pool error:",
      error
    );

    state.outreachAcceptedPool = {
      summary: {
        total: 0,
        not_sent: 0,
        sent: 0
      },
      items: []
    };
  }
}


// ---------------------------------------------------------
// MESSAGE PREPARATION
// ---------------------------------------------------------


async function loadMessagePreparation() {
  try {
    const response = await fetch(
      "/api/outreach/messages/preparation",
      {
        method: "GET",
        headers: {
          "Accept": "application/json"
        },
        cache: "no-store"
      }
    );

    const result = await response.json();

    if (!response.ok || !result.ok) {
      throw new Error(
        result.detail ||
        result.error ||
        "Could not load message preparation."
      );
    }

    const preparation =
      result.preparation || {};

    state.messagePreparation = {
      count: Number(preparation.count || 0),
      items: Array.isArray(preparation.items)
        ? preparation.items
        : []
    };

    reconcileAcceptedPoolSelection();

    if (els.messagePreparationError) {
      els.messagePreparationError.hidden = true;
      els.messagePreparationError.textContent = "";
    }
  } catch (error) {
    console.error("Message preparation error:", error);

    state.messagePreparation = {
      count: 0,
      items: []
    };

    if (els.messagePreparationError) {
      els.messagePreparationError.hidden = false;
      els.messagePreparationError.textContent =
        error.message || String(error);
    }
  }
}


async function loadMessageBatches() {
  try {
    const response = await fetch(
      "/api/outreach/messages/batches",
      {
        method: "GET",
        headers: {
          "Accept": "application/json"
        },
        cache: "no-store"
      }
    );

    const result = await response.json();

    if (!response.ok || !result.ok) {
      throw new Error(
        result.detail ||
        result.error ||
        "Could not load prepared batches."
      );
    }

    state.messageBatches =
      Array.isArray(result.batches)
        ? result.batches
        : [];
  } catch (error) {
    console.error("Message batch list error:", error);
    state.messageBatches = [];
  }
}


function getMessageBatchSendLabel(
  batchStatus,
  queueSubmitting
) {
  if (queueSubmitting) {
    return "Queueing...";
  }

  if (batchStatus === "queued") {
    return "Queued";
  }

  if (batchStatus === "processing") {
    return "Sending...";
  }

  if (batchStatus === "completed") {
    return "Completed";
  }

  if (batchStatus === "failed") {
    return "Failed";
  }

  return "Send messages";
}



function getMessageBatchSourceConnectIds(
  batch
) {
  return Array.isArray(
    batch?.source_connect_ids
  )
    ? batch.source_connect_ids.filter(
        (item) =>
          String(
            item?.id ||
            ""
          ).trim()
      )
    : [];
}


function getMessageBatchSourceLabel(
  source
) {
  const code =
    String(
      source?.batch_label ||
      source?.display_name ||
      source?.code ||
      ""
    ).trim();

  if (code) {
    return code;
  }

  const id =
    String(
      source?.id ||
      ""
    ).trim();

  if (!id) {
    return "Unknown";
  }

  return id.length > 16
    ? `${id.slice(0, 8)}…${id.slice(-5)}`
    : id;
}

function getMessageBatchSourceTooltipLine(source) {
  const code = String(source?.code || source?.id || "").trim();
  const name = String(source?.batch_label || source?.display_name || "").trim();

  return code && name
    ? `${code} - ${name}`
    : code || name || "Unknown Connect Job";
}

function renderMessageBatchSourceFilter() {
  const select =
    els.messageBatchSourceFilter;

  if (!select) {
    return;
  }

  const sourcesById =
    new Map();

  (
    Array.isArray(state.messageBatches)
      ? state.messageBatches
      : []
  ).forEach((batch) => {
    getMessageBatchSourceConnectIds(
      batch
    ).forEach((source) => {
      const id =
        String(
          source.id ||
          ""
        ).trim();

      if (!id) {
        return;
      }

      sourcesById.set(
        id,
        getMessageBatchSourceLabel(
          source
        )
      );
    });
  });

  const sortedSources =
    Array.from(
      sourcesById.entries()
    ).sort(
      (left, right) =>
        right[1].localeCompare(
          left[1],
          undefined,
          {
            numeric: true,
            sensitivity: "base"
          }
        )
    );

  const current =
    state.messageBatchSourceFilter ||
    "all";

  const fragment =
    document.createDocumentFragment();

  const allOption =
    document.createElement(
      "option"
    );

  allOption.value =
    "all";

  allOption.textContent =
    "All Connect IDs";

  fragment.append(
    allOption
  );

  sortedSources.forEach(
    ([id, label]) => {
      const option =
        document.createElement(
          "option"
        );

      option.value =
        id;

      option.textContent =
        label;

      fragment.append(
        option
      );
    }
  );

  select.replaceChildren(
    fragment
  );

  const stillExists =
    current === "all" ||
    sourcesById.has(
      current
    );

  state.messageBatchSourceFilter =
    stillExists
      ? current
      : "all";

  select.value =
    state.messageBatchSourceFilter;
}


function getFilteredMessageBatches() {
  const batches =
    Array.isArray(state.messageBatches)
      ? state.messageBatches
      : [];

  if (!state.messageBatchWeekKey) {
    return [];
  }

  const sourceFilter =
    state.messageBatchSourceFilter ||
    "all";

  return batches.filter(
    (batch) => {
      const week = getWeekInfo(
        batch?.created_at ||
        batch?.prepared_at ||
        batch?.createdAt
      );

      const weekMatches =
        week?.key === state.messageBatchWeekKey;

      const sourceMatches =
        sourceFilter === "all" ||
        getMessageBatchSourceConnectIds(
          batch
        ).some(
          (source) =>
            String(
              source.id ||
              ""
            ).trim() ===
            sourceFilter
        );

      return weekMatches && sourceMatches;
    }
  );
}


function getMessageBatchWeekGroups() {
  const groups = new Map();

  (Array.isArray(state.messageBatches)
    ? state.messageBatches
    : []
  ).forEach((batch) => {
    const info = getWeekInfo(
      batch?.created_at ||
      batch?.prepared_at ||
      batch?.createdAt
    );

    if (!info) {
      return;
    }

    if (!groups.has(info.key)) {
      groups.set(info.key, {
        ...info,
        batches: 0,
        recipients: 0,
        completed: 0
      });
    }

    const group = groups.get(info.key);
    group.batches += 1;
    group.recipients += Number(batch.target_count || 0);

    if (normaliseStatus(batch.status || "prepared") === "completed") {
      group.completed += 1;
    }
  });

  return Array.from(groups.values()).sort(
    (left, right) => right.start - left.start
  );
}


function renderMessageBatchWeekOption(group, selectedKey, currentKey) {
  const option = document.createElement("button");
  option.type = "button";
  option.className = "message-week-option";
  option.dataset.messageBatchWeekOption = group.key;
  option.setAttribute("aria-pressed", String(group.key === selectedKey));
  option.innerHTML = `
    <span class="message-week-option-copy">
      <strong>${escapeHtml(group.label)}${group.key === currentKey ? " · Current" : ""}</strong>
      <small>${group.batches} batches · ${group.recipients} recipients</small>
    </span>
    <span class="message-week-option-check" aria-hidden="true">✓</span>
  `;
  return option;
}


function getMessageBatchWeekSelection() {
  const groups = getMessageBatchWeekGroups();
  const current = getWeekInfo(new Date());
  const requestedKey = state.messageBatchWeekKey || current?.key;
  const selectedKey = requestedKey === current?.key || groups.some(
    (group) => group.key === requestedKey
  ) ? requestedKey : current?.key;
  const selectedGroup = groups.find((group) => group.key === selectedKey);

  if (state.messageBatchWeekKey !== selectedKey) {
    state.messageBatchWeekKey = selectedKey || null;
  }

  return {
    groups,
    current,
    selected: selectedGroup || {
      ...(current || {
        key: "current",
        label: "Current week",
        start: Date.now()
      }),
      batches: 0,
      recipients: 0,
      completed: 0
    }
  };
}


function renderMessageBatchWeekList() {
  const selection = getMessageBatchWeekSelection();
  if (els.messageBatchWeekButtonLabel) {
    els.messageBatchWeekButtonLabel.textContent = selection.selected.label;
  }
  if (els.messageBatchWeekMenu) {
    const currentGroup = selection.groups.find(
      (group) => group.key === selection.current?.key
    ) || {
      ...selection.current,
      batches: 0,
      recipients: 0,
      completed: 0
    };
    const options = [
      currentGroup,
      ...selection.groups.filter((group) => group.key !== selection.current?.key)
    ];
    els.messageBatchWeekMenu.replaceChildren(
      ...options.map((group) => renderMessageBatchWeekOption(
        group, selection.selected.key, selection.current?.key
      ))
    );
  }
}


function setMessageBatchWeekMenuOpen(open, {restoreFocus = false} = {}) {
  if (!els.messageBatchWeekButton || !els.messageBatchWeekMenu) {
    return;
  }
  els.messageBatchWeekMenu.hidden = !open;
  els.messageBatchWeekButton.setAttribute("aria-expanded", String(open));
  if (!open && restoreFocus) els.messageBatchWeekButton.focus();
}



function renderMessagePreparation() {
  const count = Number(
    state.messagePreparation?.count || 0
  );

  if (els.messagePreparationCount) {
    els.messagePreparationCount.textContent =
      `${count} eligible`;

    els.messagePreparationCount.className =
      `pill ${count > 0 ? "pill-purple" : "pill-neutral"}`;
  }

  if (els.messagePreparationHeadline) {
    els.messagePreparationHeadline.textContent =
      count > 0
        ? `${count} accepted profiles ready to prepare`
        : "No recipients ready to prepare";
  }

  if (els.messagePreparationMeta) {
    els.messagePreparationMeta.textContent =
      count > 0
        ? "Prepare All creates a separate fixed message batch for each source Connect batch."
        : "Accepted profiles not yet assigned to a prepared batch appear here.";
  }

  const selectedCount =
    state.outreachAcceptedSelectedProspectIds.size;

  if (els.messagePrepareSelectedButton) {
    els.messagePrepareSelectedButton.disabled =
      state.messagePreparationSubmitting ||
      state.messagePreparationSelectedSubmitting ||
      selectedCount <= 0;

    els.messagePrepareSelectedButton.textContent =
      state.messagePreparationSelectedSubmitting
        ? "Preparing..."
        : selectedCount > 0
          ? `Prepare selected ${selectedCount}`
          : "Prepare selected";
  }

  if (els.messagePrepareAllButton) {
    els.messagePrepareAllButton.disabled =
      state.messagePreparationSubmitting ||
      state.messagePreparationSelectedSubmitting ||
      count <= 0;

    els.messagePrepareAllButton.textContent =
      state.messagePreparationSubmitting
        ? "Preparing..."
        : count > 0
          ? `Prepare all ${count}`
          : "Prepare all";
  }

  renderMessageBatchWeekList();
  renderMessageBatchSourceFilter();

  const allBatches =
    Array.isArray(state.messageBatches)
      ? state.messageBatches
      : [];

  const batches =
    getFilteredMessageBatches();

  if (els.messageBatchCount) {
    els.messageBatchCount.textContent =
      !state.messageBatchWeekKey
        ? "Select a week"
        : state.messageBatchSourceFilter === "all"
          ? `${batches.length} batches`
          : `${batches.length} of ${allBatches.length}`;
  }

  if (els.messageBatchEmpty) {
    els.messageBatchEmpty.hidden =
      batches.length > 0;

    if (!batches.length) {
      els.messageBatchEmpty.textContent =
        state.messageBatchWeekKey
          ? "No prepared batches match this week."
          : allBatches.length
            ? "Select a week to view message batches."
            : "No prepared batches yet.";
    }
  }

  if (els.messageBatchGridWrap) {
    els.messageBatchGridWrap.hidden = batches.length === 0;
  }

  if (
    !els.messageBatchList ||
    !els.messageBatchRowTemplate
  ) {
    return;
  }

  const batchPageSize = Number(
    state.messageBatchPageSize || 8
  );

  const batchTotalPages = Math.max(
    1,
    Math.ceil(batches.length / batchPageSize)
  );

  state.messageBatchPage = Math.min(
    batchTotalPages,
    Math.max(1, state.messageBatchPage)
  );

  const batchStartIndex =
    (state.messageBatchPage - 1) * batchPageSize;

  const visibleBatches = batches.slice(
    batchStartIndex,
    batchStartIndex + batchPageSize
  );

  els.messageBatchList.replaceChildren();

  visibleBatches.forEach((batch) => {
    const batchId = String(
      batch.id || ""
    ).trim();

    const batchStatus = normaliseStatus(
      batch.status || "prepared"
    );

    const queueSubmitting =
      state
        .messageBatchQueueSubmittingIds
        .has(batchId);

    const canSend =
      Boolean(batchId) &&
      batchStatus === "prepared" &&
      !queueSubmitting;

    const fragment =
      els.messageBatchRowTemplate
        .content
        .cloneNode(true);

    const code =
      fragment.querySelector(
        "[data-message-batch-code]"
      );

    const meta =
      fragment.querySelector(
        "[data-message-batch-meta]"
      );

    const recipients =
      fragment.querySelector(
        "[data-message-batch-recipients]"
      );

    const source =
      fragment.querySelector(
        "[data-message-batch-source]"
      );

    const status =
      fragment.querySelector(
        "[data-message-batch-status]"
      );

    const detailButton =
      fragment.querySelector(
        "[data-message-batch-detail]"
      );

    const sendButton =
      fragment.querySelector(
        "[data-message-batch-send]"
      );

    if (code) {
      code.textContent =
        batch.batch_code ||
        "Prepared batch";
    }

    if (meta) {
      meta.textContent =
        formatDate(batch.created_at);
    }

    if (recipients) {
      recipients.textContent =
        String(Number(batch.target_count || 0));
    }

    if (source) {
      const sourceIds =
        getMessageBatchSourceConnectIds(
          batch
        );

      if (sourceIds.length === 1) {
        const sourceItem = sourceIds[0];
        source.textContent =
          sourceItem.batch_label || `${sourceItem.display_name || "Unnamed campaign"} · ${sourceItem.code || sourceItem.id}`;

        source.title =
          `Campaign: ${sourceItem.display_name || "Unnamed campaign"}\nSource Batch ID: ${sourceItem.id}\n${getMessageBatchSourceTooltipLine(sourceItem)}`;
      } else if (sourceIds.length > 1) {
        source.textContent =
          `Mixed legacy batch · ${sourceIds.length} sources`;

        source.title =
          sourceIds
            .map(getMessageBatchSourceTooltipLine)
            .join("\n");
      } else {
        source.textContent =
          "Campaign · source batch unavailable";

        source.title =
          "Source Connect Job unavailable.";
      }
    }

    if (status) {
      status.textContent =
        batchStatus;
      status.dataset.status = batchStatus;
    }

    if (detailButton) {
      detailButton.dataset.messageBatchDetailId =
        batchId;

      detailButton.addEventListener(
        "click",
        () => {
          openPreparedMessageBatch(
            batchId
          );
        }
      );
    }

    if (sendButton) {
      sendButton.dataset.messageBatchSendId =
        batchId;

      sendButton.disabled =
        !canSend;

      sendButton.textContent =
        getMessageBatchSendLabel(
          batchStatus,
          queueSubmitting
        );

      sendButton.addEventListener(
        "click",
        () => {
          openMessageSendModal(
            batchId
          );
        }
      );
    }

    els.messageBatchList.append(
      fragment
    );
  });

  updateSimplePagination({
    container: els.messageBatchPagination,
    meta: els.messageBatchPageMeta,
    prev: els.messageBatchPrevPage,
    next: els.messageBatchNextPage,
    currentPage: state.messageBatchPage,
    totalPages: batchTotalPages,
    totalItems: batches.length,
    startIndex: batchStartIndex,
    pageLength: visibleBatches.length
  });
}


function getMessageBatchById(
  batchId
) {
  const cleanedBatchId = String(
    batchId || ""
  ).trim();

  return (
    Array.isArray(state.messageBatches)
      ? state.messageBatches
      : []
  ).find(
    (item) =>
      String(item?.id || "").trim() ===
      cleanedBatchId
  ) || null;
}


function setMessageTemplateStatus(message) {
  if (els.messageTemplateStatus) els.messageTemplateStatus.textContent = message;
}

function refreshMessageTemplateControls() {
  const batchId = state.messageSendSelectedBatchId;
  const hasText = Boolean(els.messageTemplateInput?.value.trim());
  const busy = state.messageTemplateLoading || state.messageTemplateSaving ||
    state.messageBatchQueueSubmittingIds.has(batchId);
  if (els.messageTemplateSaveButton) {
    els.messageTemplateSaveButton.disabled =
      !state.messageTemplateCanSave || !hasText || busy;
  }
  if (els.messageSendConfirmButton) {
    els.messageSendConfirmButton.disabled = !hasText || busy;
  }
}

async function loadCampaignMessageTemplate(batchId, loadVersion) {
  try {
    const response = await fetch(
      "/api/outreach/messages/batches/" + encodeURIComponent(batchId) + "/template",
      { headers: { "Accept": "application/json" }, cache: "no-store" }
    );
    const result = await response.json();
    if (!response.ok || !result.ok) {
      throw new Error(result.detail || result.error || "Could not load saved template.");
    }
    if (state.messageSendSelectedBatchId !== batchId ||
        state.messageSendLoadVersion !== loadVersion) return;

    const template = result.template || {};
    state.messageTemplateCanSave = Boolean(template.can_save);
    if (els.messageSendCampaignName && template.campaign_name) {
      els.messageSendCampaignName.textContent =
        acceptedPoolCampaignName({ campaign_name: template.campaign_name });
    }
    if (els.messageTemplateInput) {
      els.messageTemplateInput.value = template.message_template || "";
    }
    setMessageTemplateStatus(
      template.saved_at ? "Saved template loaded for this campaign" :
      template.can_save ? "No template saved for this campaign yet" :
      "This batch has no single campaign; enter a message for this batch"
    );
  } catch (error) {
    if (state.messageSendSelectedBatchId !== batchId ||
        state.messageSendLoadVersion !== loadVersion) return;
    setMessageTemplateStatus("Saved template unavailable");
    if (els.messageSendError) {
      els.messageSendError.textContent = error.message || String(error);
      els.messageSendError.hidden = false;
    }
  } finally {
    if (state.messageSendSelectedBatchId === batchId &&
        state.messageSendLoadVersion === loadVersion) {
      state.messageTemplateLoading = false;
      if (els.messageTemplateInput) els.messageTemplateInput.disabled = false;
      refreshMessageTemplateControls();
      els.messageTemplateInput?.focus();
    }
  }
}

async function saveCurrentCampaignMessageTemplate() {
  const batchId = state.messageSendSelectedBatchId;
  const loadVersion = state.messageSendLoadVersion;
  const template = els.messageTemplateInput?.value.trim() || "";
  if (!batchId || !template || !state.messageTemplateCanSave) return;
  state.messageTemplateSaving = true;
  refreshMessageTemplateControls();
  if (els.messageTemplateSaveButton) {
    els.messageTemplateSaveButton.textContent = "Saving...";
  }
  if (els.messageSendError) els.messageSendError.hidden = true;
  try {
    const response = await fetch(
      "/api/outreach/messages/batches/" + encodeURIComponent(batchId) + "/template",
      {
        method: "POST",
        headers: { "Accept": "application/json", "Content-Type": "application/json" },
        cache: "no-store",
        body: JSON.stringify({ message_template: template })
      }
    );
    const result = await response.json();
    if (!response.ok || !result.ok) {
      throw new Error(result.detail || result.error || "Could not save template.");
    }
    if (state.messageSendSelectedBatchId === batchId &&
        state.messageSendLoadVersion === loadVersion) {
      setMessageTemplateStatus(
        els.messageTemplateInput?.value.trim() === template
          ? "Template saved for this campaign"
          : "Saved previous draft · New changes are unsaved"
      );
    }
  } catch (error) {
    if (state.messageSendSelectedBatchId === batchId &&
        state.messageSendLoadVersion === loadVersion) {
      setMessageTemplateStatus("Template was not saved");
      if (els.messageSendError) {
        els.messageSendError.textContent = error.message || String(error);
        els.messageSendError.hidden = false;
      }
    }
  } finally {
    if (state.messageSendSelectedBatchId === batchId &&
        state.messageSendLoadVersion === loadVersion) {
      state.messageTemplateSaving = false;
      if (els.messageTemplateSaveButton) {
        els.messageTemplateSaveButton.textContent = "Save template";
      }
      refreshMessageTemplateControls();
    }
  }
}

function openMessageSendModal(
  batchId
) {
  const batch = getMessageBatchById(
    batchId
  );

  if (!batch) {
    return;
  }

  if (
    normaliseStatus(batch.status) !==
    "prepared"
  ) {
    return;
  }

  state.messageSendSelectedBatchId =
    String(batch.id || "").trim();
  state.messageSendLoadVersion += 1;
  state.messageTemplateLoading = true;
  state.messageTemplateCanSave = Boolean(batch.campaign_id);
  const loadVersion = state.messageSendLoadVersion;

  if (els.messageSendDialogMeta) {
    els.messageSendDialogMeta.textContent =
      `${batch.batch_code || "Message batch"} · ${Number(
        batch.target_count || 0
      )} recipients`;
  }

  if (els.messageSendCampaignName) {
    els.messageSendCampaignName.textContent = batch.campaign_id
      ? acceptedPoolCampaignName({ campaign_name: batch.campaign_name })
      : "Mixed source batch";
  }
  if (els.messageTemplateInput) {
    els.messageTemplateInput.value = "";
    els.messageTemplateInput.disabled = true;
  }
  setMessageTemplateStatus("Loading saved template...");

  if (els.messageSendError) {
    els.messageSendError.hidden = true;
    els.messageSendError.textContent = "";
  }

  if (els.messageSendModal) {
    els.messageSendModal.hidden = false;
  }
  refreshMessageTemplateControls();
  void loadCampaignMessageTemplate(state.messageSendSelectedBatchId, loadVersion);
}


function closeMessageSendModal() {
  state.messageSendSelectedBatchId =
    null;
  state.messageSendLoadVersion += 1;
  state.messageTemplateLoading = false;
  state.messageTemplateSaving = false;
  state.messageTemplateCanSave = false;
  if (els.messageTemplateSaveButton) {
    els.messageTemplateSaveButton.textContent = "Save template";
  }

  if (els.messageSendError) {
    els.messageSendError.hidden = true;
    els.messageSendError.textContent = "";
  }

  if (els.messageSendModal) {
    els.messageSendModal.hidden = true;
  }
}


async function queueMessageBatchForSending(
  batchId,
  messageTemplate
) {
  const cleanedBatchId = String(
    batchId || ""
  ).trim();

  const cleanedTemplate = String(
    messageTemplate || ""
  ).trim();

  if (!cleanedBatchId) {
    throw new Error(
      "Message Batch ID not found."
    );
  }

  if (!cleanedTemplate) {
    throw new Error(
      "Message template cannot be empty."
    );
  }

  if (
    state
      .messageBatchQueueSubmittingIds
      .has(cleanedBatchId)
  ) {
    return;
  }

  const batch = getMessageBatchById(
    cleanedBatchId
  );

  if (!batch) {
    throw new Error(
        "Message Batch not found."
    );
  }

  if (
    normaliseStatus(batch.status) !==
    "prepared"
  ) {
    throw new Error(
        "Only prepared batches can be sent."
    );
  }

  state
    .messageBatchQueueSubmittingIds
    .add(cleanedBatchId);

  if (els.messageSendConfirmButton) {
    els.messageSendConfirmButton.disabled =
      true;

    els.messageSendConfirmButton.textContent =
      "Queueing...";
  }
  setMessageTemplateStatus("Queueing batch and saving template...");
  refreshMessageTemplateControls();

  renderMessagePreparation();

  try {
    const response = await fetch(
      `/api/outreach/messages/batches/${encodeURIComponent(
        cleanedBatchId
      )}/queue`,
      {
        method: "POST",
        headers: {
          "Accept": "application/json",
          "Content-Type": "application/json"
        },
        cache: "no-store",
        body: JSON.stringify({
          message_template: cleanedTemplate
        })
      }
    );

    const result = await response.json();

    if (
      !response.ok ||
      !result.ok
    ) {
      throw new Error(
        result.detail ||
        result.error ||
        "Could not queue the Message Batch."
      );
    }

    closeMessageSendModal();

    await Promise.all([
      loadMessageBatches(),
      loadMessagePreparation()
    ]);

  } finally {
    state
      .messageBatchQueueSubmittingIds
      .delete(cleanedBatchId);

    if (els.messageSendConfirmButton) {
      els.messageSendConfirmButton.disabled =
        false;

      els.messageSendConfirmButton.textContent =
        "Queue & Send";
    }

    refreshMessageTemplateControls();

    renderMessagePreparation();
  }
}


async function openPreparedMessageBatch(batchId) {
  if (!batchId) {
    return;
  }

  try {
    const response = await fetch(
      `/api/outreach/messages/batches/${encodeURIComponent(batchId)}`,
      {
        method: "GET",
        headers: {
          "Accept": "application/json"
        },
        cache: "no-store"
      }
    );

    const result = await response.json();

    if (!response.ok || !result.ok) {
      throw new Error(
        result.detail ||
        result.error ||
        "Could not load the prepared batch."
      );
    }

    const batch = result.batch || {};
    const targets =
      Array.isArray(batch.targets)
        ? batch.targets
        : [];

    if (els.drawerName) {
      els.drawerName.textContent =
        batch.batch_code || "Prepared Message Batch";
    }

    if (els.drawerContent) {
      els.drawerContent.innerHTML = `
        <div class="drawer-section">
          <p class="panel-meta">
            ${escapeHtml(String(batch.target_count || targets.length))}
            recipients · ${escapeHtml(batch.status || "prepared")}
          </p>
        </div>

        <div class="drawer-section">
          ${targets.length
            ? targets.map((target) => `
                <div class="detail-row">
                  <span>${escapeHtml(
                    getOutreachAccountDisplayName(
                      target.assigned_account_id
                    )
                  )}</span>
                  <div>
                  <a
                    href="${escapeHtml(target.linkedin_url || "")}"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    ${escapeHtml(target.linkedin_url || "—")}
                  </a>
                  <p class="panel-meta">Company: ${escapeHtml(target.company_name || "Not saved")}</p>
                  </div>
                </div>
              `).join("")
            : '<div class="state">This batch has no recipients.</div>'
          }
        </div>
      `;
    }

    if (els.drawerBackdrop) {
      els.drawerBackdrop.hidden = false;
    }

    if (els.detailDrawer) {
      els.detailDrawer.classList.add("is-open");
      els.detailDrawer.setAttribute("aria-hidden", "false");
    }

    // The snapshot drawer owns vertical scrolling while it is open.
    document.body.style.overflow = "hidden";
  } catch (error) {
    window.alert(
      error.message || String(error)
    );
  }
}


function openMessagePrepareConfirmModal(
  mode
) {
  const selectedCount =
    state.outreachAcceptedSelectedProspectIds.size;

  const eligibleCount =
    Number(
      state.messagePreparation?.count || 0
    );

  const count =
    mode === "selected"
      ? selectedCount
      : eligibleCount;

  if (count <= 0) {
    return;
  }

  state.messagePrepareConfirmMode =
    mode;

  if (els.messagePrepareConfirmTitle) {
    els.messagePrepareConfirmTitle.textContent =
      mode === "selected"
        ? "Prepare selected recipients"
        : "Prepare all recipients";
  }

  if (els.messagePrepareConfirmMeta) {
    els.messagePrepareConfirmMeta.textContent =
      mode === "selected"
        ? `${count} selected accepted profiles`
        : `${count} currently eligible accepted profiles`;
  }

  if (els.messagePrepareConfirmButton) {
    els.messagePrepareConfirmButton.textContent =
      mode === "selected"
        ? `Prepare selected ${count}`
        : `Prepare all ${count}`;
  }

  if (els.messagePrepareConfirmError) {
    els.messagePrepareConfirmError.hidden =
      true;

    els.messagePrepareConfirmError.textContent =
      "";
  }

  if (els.messagePrepareConfirmModal) {
    els.messagePrepareConfirmModal.hidden =
      false;
  }
}


function closeMessagePrepareConfirmModal() {
  state.messagePrepareConfirmMode =
    null;

  if (els.messagePrepareConfirmError) {
    els.messagePrepareConfirmError.hidden =
      true;

    els.messagePrepareConfirmError.textContent =
      "";
  }

  if (els.messagePrepareConfirmModal) {
    els.messagePrepareConfirmModal.hidden =
      true;
  }
}


async function confirmMessagePreparation() {
  const mode =
    state.messagePrepareConfirmMode;

  if (mode === "selected") {
    await prepareSelectedMessageRecipients(
      true
    );

    return;
  }

  if (mode === "all") {
    await prepareAllMessageRecipients(
      true
    );
  }
}


async function prepareSelectedMessageRecipients(
  confirmed = false
) {
  const prospectIds =
    Array.from(
      state.outreachAcceptedSelectedProspectIds
    );

  if (
    !prospectIds.length ||
    state.messagePreparationSubmitting ||
    state.messagePreparationSelectedSubmitting
  ) {
    return;
  }

  if (!confirmed) {
    openMessagePrepareConfirmModal(
      "selected"
    );

    return;
  }

  state.messagePreparationSelectedSubmitting =
    true;

  if (els.messagePrepareConfirmButton) {
    els.messagePrepareConfirmButton.disabled =
      true;

    els.messagePrepareConfirmButton.textContent =
      "Preparing...";
  }

  renderMessagePreparation();

  try {
    const response = await fetch(
      "/api/outreach/messages/prepare-selected",
      {
        method: "POST",
        headers: {
          "Accept": "application/json",
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          prospect_ids: prospectIds
        })
      }
    );

    const result = await response.json();

    if (!response.ok || !result.ok) {
      throw new Error(
        result.detail ||
        result.error ||
        "Could not prepare selected recipients."
      );
    }

    state
      .outreachAcceptedSelectedProspectIds
      .clear();

    closeMessagePrepareConfirmModal();

    await Promise.all([
      loadOutreachAcceptedPool(),
      loadMessagePreparation(),
      loadMessageBatches()
    ]);

    renderOutreachAcceptedPool();

  } catch (error) {
    if (els.messagePrepareConfirmError) {
      els.messagePrepareConfirmError.hidden =
        false;

      els.messagePrepareConfirmError.textContent =
        error.message ||
        String(error);
    }

    if (els.messagePreparationError) {
      els.messagePreparationError.hidden =
        false;

      els.messagePreparationError.textContent =
        error.message ||
        String(error);
    }

  } finally {
    state.messagePreparationSelectedSubmitting =
      false;

    if (els.messagePrepareConfirmButton) {
      els.messagePrepareConfirmButton.disabled =
        false;
    }

    renderMessagePreparation();
  }
}


async function prepareAllMessageRecipients(
  confirmed = false
) {
  const count = Number(
    state.messagePreparation?.count || 0
  );

  if (
    count <= 0 ||
    state.messagePreparationSubmitting ||
    state.messagePreparationSelectedSubmitting
  ) {
    return;
  }

  if (!confirmed) {
    openMessagePrepareConfirmModal(
      "all"
    );

    return;
  }

  state.messagePreparationSubmitting =
    true;

  if (els.messagePrepareConfirmButton) {
    els.messagePrepareConfirmButton.disabled =
      true;

    els.messagePrepareConfirmButton.textContent =
      "Preparing...";
  }

  renderMessagePreparation();

  try {
    const response = await fetch(
      "/api/outreach/messages/prepare-all",
      {
        method: "POST",
        headers: {
          "Accept": "application/json"
        }
      }
    );

    const result = await response.json();

    if (!response.ok || !result.ok) {
      throw new Error(
        result.detail ||
        result.error ||
        "Could not prepare recipients."
      );
    }

    closeMessagePrepareConfirmModal();

    await Promise.all([
      loadOutreachAcceptedPool(),
      loadMessagePreparation(),
      loadMessageBatches()
    ]);

    renderOutreachAcceptedPool();

  } catch (error) {
    if (els.messagePrepareConfirmError) {
      els.messagePrepareConfirmError.hidden =
        false;

      els.messagePrepareConfirmError.textContent =
        error.message ||
        String(error);
    }

    if (els.messagePreparationError) {
      els.messagePreparationError.hidden =
        false;

      els.messagePreparationError.textContent =
        error.message ||
        String(error);
    }

  } finally {
    state.messagePreparationSubmitting =
      false;

    if (els.messagePrepareConfirmButton) {
      els.messagePrepareConfirmButton.disabled =
        false;
    }

    renderMessagePreparation();
  }
}


// ---------------------------------------------------------
// CONNECT HISTORY — GROUPED BY LOCAL CALENDAR WEEK
// ---------------------------------------------------------

function connectWeekStart(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: "Asia/Ho_Chi_Minh",
    year: "numeric", month: "2-digit", day: "2-digit"
  }).formatToParts(date);
  const number = (type) => Number(parts.find((part) => part.type === type)?.value);
  const localDay = new Date(Date.UTC(number("year"), number("month") - 1, number("day")));
  localDay.setUTCDate(localDay.getUTCDate() - (localDay.getUTCDay() + 6) % 7);
  return localDay;
}

function connectDayKey(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: "Asia/Ho_Chi_Minh",
    year: "numeric", month: "2-digit", day: "2-digit"
  }).formatToParts(date);
  const part = (type) => parts.find((item) => item.type === type)?.value || "";
  return `${part("year")}-${part("month")}-${part("day")}`;
}

function connectDayLabel(key) {
  const [year, month, day] = key.split("-");
  return `${day}/${month}/${year}`;
}

function connectWeekTitle(start) {
  const month = new Intl.DateTimeFormat("en-US", {
    timeZone: "UTC", month: "long"
  }).format(start);
  const firstOfMonth = new Date(Date.UTC(
    start.getUTCFullYear(),
    start.getUTCMonth(),
    1
  ));
  const mondayOffset = (firstOfMonth.getUTCDay() + 6) % 7;
  const weekNumber = Math.floor(
    (start.getUTCDate() + mondayOffset - 1) / 7
  ) + 1;
  return `Week ${weekNumber} of ${month}`;
}

function renderConnectHistory(jobs) {
  const container = els.connectHistoryWeeks;
  if (!container) return;
  const allRows = Array.isArray(jobs) ? jobs : [];
  const filter = els.connectHistoryCampaignFilter;
  if (filter) {
    const campaigns = new Map();
    for (const job of allRows) {
      const id = String(job.campaign_id || "").trim();
      if (id && !campaigns.has(id)) campaigns.set(id, acceptedPoolCampaignName({campaign_name: job.display_name}));
    }
    const options = [...campaigns.entries()].sort((left, right) => left[1].localeCompare(right[1]));
    const currentIds = [...filter.options].slice(1).map((option) => option.value);
    if (options.map(([id]) => id).join("\u0000") !== currentIds.join("\u0000")) {
      const selected = filter.value;
      filter.replaceChildren(new Option("All campaigns", ""));
      for (const [id, name] of options) filter.add(new Option(name, id));
      filter.value = campaigns.has(selected) ? selected : "";
    }
  }
  renderConnectDropdown(connectDropdowns[1]);
  const campaignRows = filter?.value
    ? allRows.filter((job) => String(job.campaign_id || "").trim() === filter.value)
    : allRows;
  const dateFilter = els.connectHistoryDateFilter;
  if (dateFilter) {
    const days = [...new Set(campaignRows.map((job) => connectDayKey(job.created_at)).filter(Boolean))].sort().reverse();
    const currentDays = [...dateFilter.options].slice(1).map((option) => option.value);
    if (days.join("\u0000") !== currentDays.join("\u0000")) {
      const selected = dateFilter.value;
      dateFilter.replaceChildren(new Option("All dates", ""));
      for (const day of days) dateFilter.add(new Option(connectDayLabel(day), day));
      dateFilter.value = days.includes(selected) ? selected : "";
    }
  }
  renderConnectDropdown(connectDropdowns[4]);
  const rows = dateFilter?.value
    ? campaignRows.filter((job) => connectDayKey(job.created_at) === dateFilter.value)
    : campaignRows;
  if (els.connectHistoryCount) {
    els.connectHistoryCount.textContent = `${rows.length} ${rows.length === 1 ? "run" : "runs"}`;
  }
  container.replaceChildren();

  const weeks = new Map();
  rows.forEach((job) => {
    const start = connectWeekStart(job.created_at);
    const key = start ? start.toISOString().slice(0, 10) : "unknown";
    if (!weeks.has(key)) weeks.set(key, { start, jobs: [] });
    weeks.get(key).jobs.push(job);
  });
  const thisWeekKey = connectWeekStart(new Date())?.toISOString().slice(0, 10);
  if (!filter?.value && !dateFilter?.value && thisWeekKey && !weeks.has(thisWeekKey)) {
    weeks.set(thisWeekKey, {
      start: connectWeekStart(new Date()), jobs: []
    });
  }
  if (state.expandedConnectWeekKey === null ||
      (state.expandedConnectWeekKey !== "" && !weeks.has(state.expandedConnectWeekKey))) {
    state.expandedConnectWeekKey = [...weeks.keys()].sort().reverse()[0] || null;
  }
  const shortDate = (date) => new Intl.DateTimeFormat("en-US", {
    timeZone: "UTC", month: "short", day: "numeric"
  }).format(date);

  if (!weeks.size) {
    const empty = document.createElement("p");
    empty.className = "connect-history-empty";
    empty.textContent = "No Connect batches match these filters.";
    container.append(empty);
    return;
  }

  Array.from(weeks.entries()).sort(([a], [b]) => b.localeCompare(a)).forEach(([key, { start, jobs: weekJobs }]) => {
    const section = document.createElement("section");
    section.className = "connect-history-week";
    const heading = document.createElement("button");
    heading.type = "button";
    heading.className = "connect-history-week-toggle";
    const headingCopy = document.createElement("span");
    headingCopy.className = "connect-history-week-copy";
    const title = document.createElement("strong");
    const dateRange = document.createElement("span");
    if (start) {
      const end = new Date(start);
      end.setUTCDate(end.getUTCDate() + 6);
      title.textContent = connectWeekTitle(start);
      dateRange.textContent = `${shortDate(start)} – ${shortDate(end)}, ${end.getUTCFullYear()}`;
    } else {
      title.textContent = "Date unknown";
      dateRange.textContent = "";
    }
    headingCopy.append(title, dateRange);
    const list = document.createElement("div");
    list.className = "connect-history-list";
    const expanded = state.expandedConnectWeekKey === key;
    section.classList.toggle("is-expanded", expanded);
    section.classList.toggle("is-current", key === thisWeekKey);
    heading.setAttribute("aria-expanded", String(expanded));
    list.hidden = !expanded;
    const count = document.createElement("span");
    count.className = "connect-history-week-count";
    count.textContent = `${weekJobs.length} ${weekJobs.length === 1 ? "run" : "runs"}`;
    const chevron = document.createElement("span");
    chevron.className = "connect-history-week-chevron";
    chevron.setAttribute("aria-hidden", "true");
    chevron.textContent = expanded ? "⌄" : "›";
    heading.append(headingCopy, count, chevron);
    heading.addEventListener("click", () => {
      state.expandedConnectWeekKey = expanded ? "" : key;
      renderConnectHistory(state.outreachRecentJobs);
    });
    if (!weekJobs.length) {
      const empty = document.createElement("p");
      empty.className = "connect-history-empty";
      empty.textContent = "No Connect runs this week yet.";
      list.append(empty);
    }
    let previousDay = "";
    weekJobs.sort((left, right) => new Date(right.created_at) - new Date(left.created_at)).forEach((job) => {
      const day = connectDayKey(job.created_at);
      if (day !== previousDay) {
        const dayHeading = document.createElement("p");
        dayHeading.className = "connect-history-day-heading";
        dayHeading.textContent = day ? `Batch ${connectDayLabel(day)}` : "Date unknown";
        list.append(dayHeading);
        previousDay = day;
      }
      const button = document.createElement("button");
      button.type = "button";
      button.className = "connect-history-run";
      button.classList.toggle("is-selected", state.selectedConnectHistoryJobId === job.id);
      button.setAttribute("aria-pressed", String(state.selectedConnectHistoryJobId === job.id));
      const name = document.createElement("span");
      name.className = "connect-history-run-name";
      name.textContent = getConnectCampaignLabel(job) || "Unnamed run";
      const status = document.createElement("span");
      status.className = "connect-history-run-status";
      status.textContent = statusLabel(job.status || "pending");
      status.classList.toggle("is-completed", String(job.status || "").toLowerCase() === "completed");
      const meta = document.createElement("span");
      meta.className = "connect-history-run-meta";
      const created = document.createElement("span");
      created.textContent = formatDate(job.created_at);
      const profiles = document.createElement("span");
      profiles.textContent = `${Number(job.input_count || 0)} prospects added`;
      const processed = document.createElement("span");
      processed.textContent = `${Number(job.processed_count || 0)} processed`;
      const success = document.createElement("span");
      success.textContent = `${Number(job.success_count || 0)} success`;
      const failed = document.createElement("span");
      failed.textContent = `${Number(job.failed_count || 0)} failed`;
      meta.append(created, profiles, processed, success, failed);
      button.append(name, status, meta);
      if (String(job.status || "").toLowerCase() === "running") {
        const total = Math.max(0, Number(job.target_count) || 0);
        const successCount = Math.max(0, Number(job.success_count) || 0);
        const failedCount = Math.max(0, Number(job.failed_count) || 0);
        const successPercent = total > 0
          ? Math.min(100, (successCount / total) * 100)
          : 0;
        const failedPercent = total > 0
          ? Math.min(100 - successPercent, (failedCount / total) * 100)
          : 0;
        const progress = document.createElement("span");
        progress.className = "connect-history-progress";
        progress.setAttribute("role", "progressbar");
        progress.setAttribute("aria-label", "Connect run progress");
        progress.setAttribute("aria-valuemin", "0");
        progress.setAttribute("aria-valuemax", String(total));
        progress.setAttribute("aria-valuenow", String(Math.min(
          total, Math.max(0, Number(job.processed_count) || 0)
        )));
        const successSegment = document.createElement("span");
        successSegment.className = "connect-history-progress-success";
        successSegment.style.width = `${successPercent}%`;
        const failedSegment = document.createElement("span");
        failedSegment.className = "connect-history-progress-failed";
        failedSegment.style.width = `${failedPercent}%`;
        progress.append(successSegment, failedSegment);
        button.append(progress);
      }
      button.addEventListener("click", () => {
        state.selectedConnectHistoryJobId = state.selectedConnectHistoryJobId === job.id
          ? null : job.id;
        renderConnectHistory(state.outreachRecentJobs);
        renderOutreachJob(state.selectedConnectHistoryJobId ? job : null);
      });
      list.append(button);
    });
    section.append(heading, list);
    container.append(section);
  });
}

// ---------------------------------------------------------
// FULL DASHBOARD RENDER
// ---------------------------------------------------------


function renderOutreachDashboard() {
  populateAcceptanceInsightsJobFilter();

  renderOutreachJob(
    state.outreachRecentJobs.find(
      (job) => job.id === state.selectedConnectHistoryJobId
    ) || null
  );

  renderOutreachScheduler(
    state.outreachScheduler
  );

  renderOutreachAccounts(
    state.outreachAccounts
  );

  renderOutreachHistory(
    state.outreachRecentJobs
  );

  renderConnectHistory(state.outreachRecentJobs);

  renderOutreachAcceptanceJobs(
    state.outreachRecentJobs
  );

  renderOutreachAcceptedPool();
  renderMessagePreparation();

  if (els.outreachDashboardUpdatedAt) {
    els.outreachDashboardUpdatedAt.textContent =
      `Updated ${formatDate(
        new Date().toISOString()
      )}`;
  }
}


// ---------------------------------------------------------
// LOAD DASHBOARD
// ---------------------------------------------------------


function setOutreachDatabaseStatus(healthy, message) {
  if (!els.systemBadge || !els.systemBadgeText) {
    return;
  }

  els.systemBadge.className = `system-badge ${healthy ? "is-healthy" : "is-unhealthy"}`;
  els.systemBadgeText.textContent = message;
}

function renderWorkerActivity() {
  const activity = state.workerActivity;
  const button = els.workerActivityButton;
  if (!button) return;

  const count = Number(activity?.active_count || 0);
  const complete = activity?.complete === true;
  const mode = count > 0 ? "active" : complete ? "idle" : "unknown";
  button.classList.toggle("is-active", mode === "active");
  button.classList.toggle("is-idle", mode === "idle");
  button.classList.toggle("is-unknown", mode === "unknown");
  button.setAttribute("aria-label", count > 0
    ? `Worker activity: ${count} running`
    : complete ? "Worker activity: online, no active tasks" : "Worker activity: status unavailable");

  if (els.workerActivitySummary) {
    els.workerActivitySummary.textContent = count > 0
      ? `${count} task${count === 1 ? "" : "s"} running`
      : complete ? "Online · No active tasks" : "Status partially unavailable";
  }
  if (els.workerActivityList) {
    const tasks = Array.isArray(activity?.tasks) ? activity.tasks : [];
    els.workerActivityList.innerHTML = tasks.length
      ? tasks.map((task) => {
          const taskCount = task.count;
          const status = taskCount === null ? "Unavailable" : taskCount > 0 ? `${taskCount} running` : "Idle";
          const details = taskCount > 0 && Array.isArray(task.details)
            ? ` · ${task.details.filter(Boolean).join(", ")}` : "";
          return `<div class="worker-activity-row ${taskCount === null ? "is-unknown" : taskCount > 0 ? "is-active" : ""}"><span title="${escapeHtml(task.label + details)}">${escapeHtml(task.label + details)}</span><em>${escapeHtml(status)}</em></div>`;
        }).join("")
      : `<div class="worker-activity-row"><span>Checking worker status…</span></div>`;
  }
  if (els.workerActivityNote) {
    els.workerActivityNote.hidden = complete;
    els.workerActivityNote.textContent = "Some worker states could not be checked. Green is shown only when every source is available.";
  }
}

async function loadWorkerActivity() {
  if (state.workerActivityLoading) return;
  state.workerActivityLoading = true;
  try {
    const response = await fetch("/api/outreach/worker-activity", { cache: "no-store" });
    const result = await response.json();
    if (!response.ok || !result.ok) throw new Error(result.error || "Worker status unavailable");
    state.workerActivity = result.activity;
  } catch (error) {
    console.error("Worker activity error:", error);
    state.workerActivity = null;
  } finally {
    state.workerActivityLoading = false;
    renderWorkerActivity();
  }
}

function closeWorkerActivity() {
  if (!els.workerActivityPopover) return;
  els.workerActivityPopover.hidden = true;
  els.workerActivityButton?.setAttribute("aria-expanded", "false");
}

els.workerActivityButton?.addEventListener("click", () => {
  const opening = els.workerActivityPopover?.hidden;
  if (!els.workerActivityPopover) return;
  els.workerActivityPopover.hidden = !opening;
  els.workerActivityButton.setAttribute("aria-expanded", String(opening));
  if (opening) void loadWorkerActivity();
});
els.workerActivityClose?.addEventListener("click", closeWorkerActivity);
document.addEventListener("click", (event) => {
  if (!els.workerActivityPopover?.hidden && !els.workerActivityPopover.contains(event.target)
      && !els.workerActivityButton?.contains(event.target)) closeWorkerActivity();
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !els.workerActivityPopover?.hidden) closeWorkerActivity();
});



async function loadOutreachDashboard() {
  if (state.outreachDashboardLoading) {
    return;
  }

  state.outreachDashboardLoading = true;

  try {
    const response = await fetch(
      "/api/outreach/dashboard",
      {
        method: "GET",
        headers: {
          "Accept": "application/json"
        },
        cache: "no-store"
      }
    );

    const result =
      await response.json();

    if (
      !response.ok ||
      !result.ok
    ) {
      throw new Error(
        result.detail ||
        result.error ||
        "Could not load the Outreach dashboard."
      );
    }

    const dashboard =
      result.dashboard || {};

    state.outreachCurrentJob =
      dashboard.current_job || null;

    state.outreachScheduler =
      dashboard.scheduler || null;

    state.outreachAccounts =
      Array.isArray(
        dashboard.accounts
      )
        ? dashboard.accounts
        : [];

    state.outreachRecentJobs =
      Array.isArray(
        dashboard.recent_jobs
      )
        ? dashboard.recent_jobs
        : [];

    if (state.selectedConnectHistoryJobId && !state.outreachRecentJobs.some(
      (job) => job.id === state.selectedConnectHistoryJobId
    )) state.selectedConnectHistoryJobId = null;

    if (els.outreachError) {
      els.outreachError.hidden = true;
      els.outreachError.textContent = "";
    }

    setOutreachDatabaseStatus(true, "Database connected");

    renderOutreachDashboard();

    // Only refresh Acceptance Insights while its drawer is actually open.
    if (
      els.acceptanceInsightsDrawer?.classList.contains(
        "is-open"
      ) &&
      !state.acceptanceInsightsLoading
    ) {
      await loadAcceptanceInsights();
    }

  } catch (error) {
    console.error(
      "Outreach dashboard error:",
      error
    );

    if (els.outreachError) {
      els.outreachError.hidden = false;
      els.outreachError.textContent =
        error.message || String(error);
    }

    setOutreachDatabaseStatus(false, "Database unavailable");

  } finally {
    state.outreachDashboardLoading = false;
  }
}


async function loadOutreachProfiles() {
  if (state.outreachProfilesLoading) {
    return;
  }

  state.outreachProfilesLoading = true;

  try {
    const response = await fetch(
      "/api/outreach/profiles",
      {
        method: "GET",
        headers: {
          "Accept": "application/json"
        },
        cache: "no-store"
      }
    );

    const result =
      await response.json();

    if (
      !response.ok ||
      !result.ok
    ) {
      throw new Error(
        result.detail ||
        result.error ||
        "Could not load Outreach Profiles."
      );
    }

    state.profiles =
      Array.isArray(
        result.profiles
      )
        ? result.profiles
        : [];

    applyProfileFilters();
    updateStats();

  } catch (error) {
    console.error(
      "Outreach Profiles error:",
      error
    );

  } finally {
    state.outreachProfilesLoading = false;
  }
}


async function loadOutreachRateLimits() {
  if (state.outreachRateLimitsLoading) {
    return;
  }

  state.outreachRateLimitsLoading = true;

  try {
    const response = await fetch(
      "/api/outreach/rate-limits",
      {
        method: "GET",
        headers: {
          "Accept": "application/json"
        },
        cache: "no-store"
      }
    );

    const result =
      await response.json();

    if (
      !response.ok ||
      !result.ok
    ) {
      throw new Error(
        result.detail ||
        result.error ||
        "Could not load Rate Limits."
      );
    }

    const rateLimits =
      result.rate_limits || {};

    state.outreachScheduler =
      rateLimits.scheduler ||
      state.outreachScheduler;

    state.outreachAccounts =
      Array.isArray(
        rateLimits.accounts
      )
        ? rateLimits.accounts
        : state.outreachAccounts;

    renderOutreachScheduler(
      state.outreachScheduler
    );

    renderOutreachAccounts(
      state.outreachAccounts
    );

  } catch (error) {
    console.error(
      "Outreach Rate Limits error:",
      error
    );

  } finally {
    state.outreachRateLimitsLoading = false;
  }
}


// ---------------------------------------------------------
// POLLING
// ---------------------------------------------------------


function getOutreachPollInterval() {
  const status =
    normaliseStatus(
      state.outreachCurrentJob?.status
    );

  return (
    status === "running" ||
    status === "pending"
  )
    ? OUTREACH_ACTIVE_POLL_INTERVAL_MS
    : OUTREACH_IDLE_POLL_INTERVAL_MS;
}


function startOutreachPolling() {
  if (state.outreachPollTimer) {
    return;
  }

  const scheduleNext = () => {
    state.outreachPollTimer =
      window.setTimeout(
        async () => {
          state.outreachPollTimer = null;

          await loadOutreachDashboard();

          scheduleNext();
        },
        getOutreachPollInterval()
      );
  };

  scheduleNext();
}


// ---------------------------------------------------------
// CREATE CONNECT JOB
// ---------------------------------------------------------


async function createOutreachConnectJob(
  event
) {
  event.preventDefault();

  const enteredCampaign = selectedConnectCampaign();
  const campaignName = state.connectCampaigns.find(
    (name) => name.toLocaleLowerCase() === enteredCampaign.toLocaleLowerCase()
  ) || enteredCampaign;
  const batchName = String(els.outreachBatchName?.value || "").trim();
  if (!campaignName) {
    els.outreachCampaignTrigger?.focus();
    return;
  }

  const {urls, companyNames, error: inputError} = parseOutreachInput();
  if (inputError) {
    updateOutreachDetectedCount();
    els.outreachCompanyInput?.focus();
    return;
  }

  if (!urls.length) {
    window.alert(
      "Enter at least one LinkedIn profile URL."
    );

    return;
  }

  if (urls.length > OUTREACH_MAX_CONNECT_URLS) {
    if (els.outreachError) {
      els.outreachError.hidden = false;
      els.outreachError.textContent =
        `Maximum ${OUTREACH_MAX_CONNECT_URLS} LinkedIn profile URLs per Connect run.`;
    }
    els.outreachUrlInput?.focus();
    return;
  }


  state.outreachSubmitting = true;

  renderOutreachSubmittingState();


  if (els.outreachError) {
    els.outreachError.hidden = true;
    els.outreachError.textContent = "";
  }


  try {
    const response = await fetch(
      "/api/outreach/connect/jobs",
      {
        method: "POST",

        headers: {
          "Content-Type":
            "application/json"
        },

        body: JSON.stringify({
          urls,
          company_names: companyNames,
          campaign_name: campaignName,
          batch_name: batchName
        })
      }
    );


    const result =
      await response.json();


    if (
      !response.ok ||
      !result.ok
    ) {
      throw new Error(
        result.detail ||
        result.error ||
        "Could not create the Outreach Connect Job."
      );
    }


    state.outreachCurrentJob =
      result.job || null;

    state.selectedConnectHistoryJobId = null;


    renderOutreachJob(
      state.outreachCurrentJob
    );


    if (els.outreachUrlInput) {
      els.outreachUrlInput.value =
        "";
    }
    if (els.outreachBatchName) els.outreachBatchName.value = "";
    if (els.outreachCompanyInput) els.outreachCompanyInput.value = "";

    if (!state.connectCampaigns.some((name) => name.toLowerCase() === campaignName.toLowerCase())) {
      state.connectCampaigns.push(campaignName);
      state.connectCampaigns.sort((a, b) => a.localeCompare(b));
    }
    renderConnectCampaignOptions(campaignName);
    if (els.outreachNewCampaign) els.outreachNewCampaign.value = "";
    void loadConnectCampaigns(campaignName);


    updateOutreachDetectedCount();



    // Reload directly from the database.
    // Do not wait for the polling interval.
    await loadOutreachDashboard();


  } catch (error) {
    if (els.outreachError) {
      els.outreachError.hidden = false;

      els.outreachError.textContent =
        error.message || String(error);
    }

  } finally {
    state.outreachSubmitting = false;

    renderOutreachSubmittingState();
  }
}

function updateYoutubePolling() {
  const status = normaliseStatus(
    state.activeYoutubeJob?.status
  );
  const shouldPoll =
    status === "pending" ||
    status === "processing";

  if (shouldPoll && !state.youtubePollTimer) {
    state.youtubePollTimer = window.setInterval(
      loadYoutubeResearch,
      2000
    );
  }

  if (!shouldPoll && state.youtubePollTimer) {
    window.clearInterval(state.youtubePollTimer);
    state.youtubePollTimer = null;
  }
}


function scheduleYoutubeRealtimeReload() {
  if (state.youtubeRealtimeReloadTimer) {
    window.clearTimeout(
      state.youtubeRealtimeReloadTimer
    );
  }

  state.youtubeRealtimeReloadTimer = window.setTimeout(
    async () => {
      state.youtubeRealtimeReloadTimer = null;
      await loadYoutubeResearch();
    },
    250
  );
}

function setupYoutubeRealtime() {
  if (state.youtubeRealtimeChannel) {
    client.removeChannel(
      state.youtubeRealtimeChannel
    );
  }

  state.youtubeRealtimeChannel = client
    .channel("youtube-research-dashboard")
    .on(
      "postgres_changes",
      {
        event: "*",
        schema: "public",
        table: "youtube_scan_jobs"
      },
      scheduleYoutubeRealtimeReload
    )
    .on(
      "postgres_changes",
      {
        event: "*",
        schema: "public",
        table: "youtube_scan_channels"
      },
      scheduleYoutubeRealtimeReload
    )
    .subscribe((status) => {
      if (status === "CHANNEL_ERROR") {
        console.warn(
          "YouTube Supabase realtime channel error. " +
          "Polling fallback remains active."
        );
      }
    });
}


async function loadDashboard() {
  if (els.refreshButton) {
    els.refreshButton.disabled = true;
    els.refreshButton.querySelector(".button-icon").textContent = "…";
  }
  els.globalError.hidden = true;
  state.tableErrors = {};

  const sourceQuery = client
    .from("linkedin_sources")
    .select(
      [
        "id",
        "name",
        "linkedin_url",
        "source_type",
        "enabled",
        "job_status",
        "assigned_account_id",
        "processing_started_at",
        "processing_heartbeat_at",
        "retry_count",
        "last_error",
        "last_scanned_at",
        "completed_at",
        "lark_chat_id",
        "lark_result_sent_at",
        "lark_result_error"
      ].join(",")
    )
    .order("id", { ascending: false })
    .limit(2000);

  const accountQuery = client
    .from("linkedin_scanner_accounts")
    .select(
      [
        "account_id",
        "display_name",
        "profile_directory",
        "enabled",
        "status",
        "current_source_id",
        "batch_processed_count",
        "consecutive_failures",
        "cooldown_until",
        "last_used_at",
        "last_success_at",
        "last_error_at",
        "last_error",
        "updated_at"
      ].join(",")
    )
    .order("account_id", { ascending: true });

  const workerQuery = client
    .from("linkedin_worker_health")
    .select(
      [
        "worker_id",
        "worker_name",
        "status",
        "worker_version",
        "hostname",
        "pid",
        "current_account_id",
        "current_source_id",
        "last_heartbeat_at",
        "started_at",
        "last_batch_started_at",
        "last_batch_completed_at",
        "last_success_at",
        "last_error_at",
        "last_error",
        "updated_at"
      ].join(",")
    )
    .order("last_heartbeat_at", { ascending: false })
    .limit(1);

  const [
    sources,
    accounts,
    workers
  ] = await Promise.all([
    safeQuery("sources", sourceQuery, []),
    safeQuery("accounts", accountQuery, []),
    safeQuery("worker", workerQuery, [])
  ]);

  state.sources = sources || [];
  state.accounts = accounts || [];
  state.worker = workers?.[0] || null;

  if (els.refreshButton) {
    els.refreshButton.disabled = false;
    els.refreshButton.querySelector(".button-icon").textContent = "↻";
  }

  renderAll();
  await loadYoutubeResearch();
}

function renderAll() {
  updateStats();
  applyProfileFilters();
  applyQueueFilters();
  renderOverview();
  renderAccounts();
  renderGlobalError();
  updateWorkerControlButtons();
}

function updateStats() {
  const latestDate = state.profiles
    .map((profile) => profile.sent_at)
    .filter(Boolean)
    .sort()
    .at(-1);

  els.totalProfiles.textContent =
    state.profiles.length.toLocaleString("vi-VN");

  els.pendingCount.textContent =
    countByStatus("pending").toLocaleString("vi-VN");

  els.processingCount.textContent =
    countByStatus("processing").toLocaleString("vi-VN");

  els.completedCount.textContent =
    countByStatus("completed").toLocaleString("vi-VN");

  els.failedCount.textContent =
    countByStatus("failed").toLocaleString("vi-VN");

  els.profilesTabCount.textContent =
    state.profiles.length.toLocaleString("vi-VN");

  els.queueTabCount.textContent =
    state.sources.length.toLocaleString("vi-VN");

  els.lastUpdated.textContent =
    latestDate
      ? `Latest Connect: ${formatAge(latestDate)}`
      : "No connected profiles yet";
}

function renderGlobalError() {
  const entries = Object.entries(state.tableErrors);

  if (!entries.length) {
    els.globalError.hidden = true;
    return;
  }

  els.globalError.innerHTML = `
    <strong>Some data sources could not be read.</strong><br />
    ${entries
      .map(
        ([name, message]) =>
          `${escapeHtml(name)}: ${escapeHtml(message)}`
      )
      .join("<br />")}
  `;

  els.globalError.hidden = false;
}

function applyProfileFilters() {
  const query = els.searchInput.value
    .trim()
    .toLowerCase();

  const sort = els.sortSelect.value;

  const filtered =
    state.profiles.filter(
      (profile) => {
        const searchable = [
          profile.linkedin_url,
          profile.normalized_url,
          profile.job_code,
          profile.display_name,
          getOutreachAccountDisplayName(
            profile.assigned_account_id
          ),
          profile.connect_status,
          profile.acceptance_status,
          profile.message_status
        ]
          .filter(Boolean)
          .join(" ")
          .toLowerCase();

        return (
          !query ||
          searchable.includes(query)
        );
      }
    );

  filtered.sort((a, b) => {
    if (sort === "name") {
      return String(
        a.linkedin_url || ""
      ).localeCompare(
        String(
          b.linkedin_url || ""
        )
      );
    }

    const first =
      new Date(
        a.sent_at || 0
      ).getTime();

    const second =
      new Date(
        b.sent_at || 0
      ).getTime();

    return sort === "oldest"
      ? first - second
      : second - first;
  });

  state.filteredProfiles =
    filtered;

  renderProfileTable();
}


function renderProfileTable() {
  const profiles =
    state.filteredProfiles;

  els.resultSummary.textContent =
    `${profiles.length.toLocaleString(
      "vi-VN"
    )} sent profiles`;

  els.emptyState.hidden =
    profiles.length > 0;

  els.tableWrap.hidden =
    profiles.length === 0;

  els.profileTableBody.innerHTML =
    profiles
      .map((profile) => {
        const accountName =
          getOutreachAccountDisplayName(
            profile.assigned_account_id
          );

        const acceptanceStatus =
          String(
            profile.acceptance_status ||
            "not_checked"
          );

        const messageStatus =
          String(
            profile.message_status ||
            "not_started"
          );

        return `
          <tr>
            <td>
              <div class="profile-cell">
                <div class="avatar">
                  in
                </div>

                <div class="profile-copy">
                  <p class="profile-name">
                    ${escapeHtml(
                      profile.linkedin_url ||
                      "—"
                    )}
                  </p>

                  <p class="profile-headline">
                    ${escapeHtml(
                      profile.normalized_url ||
                      profile.linkedin_url ||
                      "—"
                    )}
                  </p>
                </div>
              </div>
            </td>

            <td>
              ${escapeHtml(
                accountName || "—"
              )}
            </td>

            <td>
              <span class="pill ${getOutreachPillClass(
                profile.connect_status
              )}">
                ${escapeHtml(
                  statusLabel(
                    profile.connect_status ||
                    "invitation_sent"
                  )
                )}
              </span>
            </td>

            <td>
              <span class="pill ${getOutreachPillClass(
                acceptanceStatus
              )}">
                ${escapeHtml(
                  statusLabel(
                    acceptanceStatus
                  )
                )}
              </span>
            </td>

            <td>
              <span class="pill ${getOutreachPillClass(
                messageStatus
              )}">
                ${escapeHtml(
                  statusLabel(
                    messageStatus
                  )
                )}
              </span>
            </td>

            <td>
              ${escapeHtml(
                profile.display_name || profile.job_code || "—"
              )}
            </td>

            <td class="muted-cell">
              ${escapeHtml(
                formatDate(
                  profile.sent_at
                )
              )}
            </td>
          </tr>
        `;
      })
      .join("");
}

function applyQueueFilters() {
  const query = els.queueSearchInput.value
    .trim()
    .toLowerCase();

  const filter = els.queueStatusFilter.value;

  state.filteredSources = state.sources.filter((source) => {
    const status = normaliseStatus(source.job_status);

    const matchesStatus =
      filter === "all" || status === filter;

    const searchable = [
      source.name,
      source.linkedin_url,
      source.assigned_account_id,
      source.job_status,
      source.last_error
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();

    return (
      matchesStatus &&
      (!query || searchable.includes(query))
    );
  });

  renderQueueTable();
}

function renderQueueTable() {
  const sources = state.filteredSources;

  els.queueSummary.textContent =
    `${sources.length.toLocaleString("vi-VN")} sources`;

  els.queueEmptyState.hidden = sources.length > 0;
  els.queueTableWrap.hidden = sources.length === 0;

  els.queueTableBody.innerHTML = sources
    .map((source) => {
      const sourceName =
        source.name ||
        `Source #${source.id}`;

      return `
        <tr>
          <td>
            <div class="queue-source">
              <strong>${escapeHtml(sourceName)}</strong>
              <span>${escapeHtml(source.linkedin_url || "—")}</span>
            </div>
          </td>

          <td>
            ${statusBadge(source.job_status)}
          </td>

          <td>
            ${escapeHtml(source.assigned_account_id || "—")}
          </td>

          <td>
            ${Number(source.retry_count || 0)}
          </td>

          <td class="muted-cell">
            ${escapeHtml(formatDate(source.processing_started_at))}
          </td>

          <td class="muted-cell">
            ${escapeHtml(formatDate(source.last_scanned_at))}
          </td>
        </tr>
      `;
    })
    .join("");
}

function getCurrentSource() {
  if (!state.worker?.current_source_id) {
    return null;
  }

  return state.sources.find(
    (source) =>
      String(source.id) ===
      String(state.worker.current_source_id)
  ) || null;
}

function renderOverview() {
  renderActiveProcess();
  renderOverviewAccounts();
  renderTimeline();
}

function renderActiveProcess() {
  const worker = state.worker;
  const source = getCurrentSource();

  if (!worker) {
    els.activeProcessBadge.className =
      "pill pill-red";
    els.activeProcessBadge.textContent =
      "Worker not registered";

    els.activeProcessContent.innerHTML = `
      <div class="empty-process">
        No worker data in linkedin_worker_health.
      </div>
    `;

    return;
  }

  const workerStatus = normaliseStatus(worker.status);

  els.activeProcessBadge.className =
    `pill ${
      workerStatus === "scanning"
        ? "pill-purple"
        : workerStatus === "idle"
          ? "pill-green"
          : "pill-amber"
    }`;

  els.activeProcessBadge.textContent =
    statusLabel(workerStatus);

  if (!source) {
    els.activeProcessContent.innerHTML = `
      <div class="active-process-card">
        <div class="active-process-title">
          <div>
            <h3>
              ${escapeHtml(
                worker.worker_name || worker.worker_id || "Mac Worker"
              )}
            </h3>
            <p class="process-url">
              No source is currently processing.
            </p>
          </div>

          ${statusBadge(worker.status)}
        </div>

        <p class="process-step">
          ${
            workerStatus === "idle"
              ? "Worker is waiting for a new URL."
              : "Worker has no current_source_id."
          }
        </p>

        <div class="active-process-footer">
          <span>
            Current account:
            ${escapeHtml(worker.current_account_id || "—")}
          </span>

          <span>
            Heartbeat ${escapeHtml(formatAge(worker.last_heartbeat_at))}
          </span>
        </div>
      </div>
    `;

    return;
  }

  const progress =
    normaliseStatus(source.job_status) === "completed"
      ? 100
      : 62;

  els.activeProcessContent.innerHTML = `
    <div class="active-process-card">
      <div class="active-process-title">
        <div>
          <h3>
            ${escapeHtml(source.name || `Source #${source.id}`)}
          </h3>

          <p class="process-url">
            ${escapeHtml(source.linkedin_url || "—")}
          </p>
        </div>

        ${statusBadge(source.job_status)}
      </div>

      <p class="process-step">
        ${
          normaliseStatus(source.job_status) === "processing"
            ? "Worker is scanning profiles and updating snapshots."
            : "Synchronizing source status."
        }
      </p>

      <div class="process-progress">
        <div
          class="process-progress-bar"
          style="width: ${progress}%"
        ></div>
      </div>

      <div class="active-process-footer">
        <span>
          ${escapeHtml(
            source.assigned_account_id ||
            worker.current_account_id ||
            "Account not assigned"
          )}
        </span>

        <span>
          Heartbeat ${escapeHtml(formatAge(worker.last_heartbeat_at))}
        </span>
      </div>
    </div>
  `;
}

function renderOverviewAccounts() {
  const enabledAccounts = state.accounts.filter(
    (account) => account.enabled !== false
  );

  const readyCount = enabledAccounts.filter(
    (account) =>
      ["available", "idle"].includes(
        normaliseStatus(account.status)
      )
  ).length;

  els.readyAccountSummary.textContent =
    `${readyCount}/${enabledAccounts.length || 0} ready`;

  if (!state.accounts.length) {
    els.overviewAccountList.innerHTML = `
      <div class="empty-process">
        Could not read linkedin_scanner_accounts.
      </div>
    `;
    return;
  }

  els.overviewAccountList.innerHTML = state.accounts
    .slice(0, 5)
    .map((account) => `
      <div class="compact-account-row">
        <div class="compact-account-copy">
          <strong>${escapeHtml(account.account_id)}</strong>
          <span>
            ${
              account.current_source_id
                ? `Source #${escapeHtml(account.current_source_id)}`
                : account.last_error
                  ? escapeHtml(account.last_error)
                  : "No current source"
            }
          </span>
        </div>

        ${statusBadge(account.status)}
      </div>
    `)
    .join("");
}

function renderTimeline() {
  const entries = [];

  if (state.worker) {
    entries.push({
      type:
        normaliseStatus(state.worker.status) === "error"
          ? "error"
          : "processing",
      icon: "W",
      title: `Worker ${statusLabel(state.worker.status)}`,
      description:
        state.worker.current_source_id
          ? `Processing source #${state.worker.current_source_id}`
          : "No current source",
      time: formatAge(state.worker.last_heartbeat_at)
    });
  }

  state.sources
    .filter((source) => source.last_scanned_at)
    .slice(0, 4)
    .forEach((source) => {
      entries.push({
        type:
          normaliseStatus(source.job_status) === "failed"
            ? "error"
            : "success",
        icon:
          normaliseStatus(source.job_status) === "failed"
            ? "!"
            : "✓",
        title:
          normaliseStatus(source.job_status) === "failed"
            ? "Source scan failed"
            : "Snapshot completed",
        description:
          source.name ||
          source.linkedin_url ||
          `Source #${source.id}`,
        time: formatAge(source.last_scanned_at)
      });
    });

  if (!entries.length) {
    els.activityTimeline.innerHTML = `
      <div class="empty-process">
        No activity to display.
      </div>
    `;
    return;
  }

  els.activityTimeline.innerHTML = entries
    .map((entry) => `
      <div class="activity-entry is-${entry.type}">
        <div class="activity-dot">${entry.icon}</div>

        <div class="activity-entry-main">
          <div class="activity-entry-copy">
            <strong>${escapeHtml(entry.title)}</strong>
            <span>${escapeHtml(entry.description)}</span>
          </div>

          <span class="activity-time">
            ${escapeHtml(entry.time)}
          </span>
        </div>
      </div>
    `)
    .join("");
}

function renderAccounts() {
  if (!state.accounts.length) {
    els.accountsGrid.innerHTML = `
      <div class="panel">
        <div class="empty-process">
          No account data, or the anon key does not have table access.
        </div>
      </div>
    `;
    return;
  }

  els.accountsGrid.innerHTML = state.accounts
    .map((account, index) => `
      <article class="account-card">
        <div class="account-card-header">
          <div class="account-title">
            <div class="account-index">
              ${String(index + 1).padStart(2, "0")}
            </div>

            <div>
              <strong>${escapeHtml(account.account_id)}</strong>
              <span>
                ${escapeHtml(
                  account.display_name || "Persistent browser session"
                )}
              </span>
            </div>
          </div>

          ${statusBadge(account.status)}
        </div>

        <div class="account-detail-list">
          <div class="account-detail-row">
            <span>Current source</span>
            <strong>
              ${
                account.current_source_id
                  ? `#${escapeHtml(account.current_source_id)}`
                  : "—"
              }
            </strong>
          </div>

          <div class="account-detail-row">
            <span>Batch processed</span>
            <strong>
              ${Number(account.batch_processed_count || 0)}
            </strong>
          </div>

          <div class="account-detail-row">
            <span>Consecutive failures</span>
            <strong>
              ${Number(account.consecutive_failures || 0)}
            </strong>
          </div>

          <div class="account-detail-row">
            <span>Last success</span>
            <strong>
              ${escapeHtml(formatAge(account.last_success_at))}
            </strong>
          </div>

          <div class="account-detail-row">
            <span>Last error</span>
            <strong>
              ${escapeHtml(account.last_error || "—")}
            </strong>
          </div>
        </div>
      </article>
    `)
    .join("");
}

function openDrawer(profile) {
  els.drawerName.textContent =
    profile.name || "Unnamed profile";

  const linkedInBlock = profile.linkedin_url
    ? `
      <a
        class="detail-link"
        href="${escapeHtml(profile.linkedin_url)}"
        target="_blank"
        rel="noreferrer"
      >
        Open LinkedIn profile
      </a>
    `
    : `
      <p>No LinkedIn URL.</p>
    `;

  const postCaptions = getPostCaptions(profile);

  const recentPostsBlock = postCaptions.length
    ? `
      <div class="recent-posts-list">
        ${postCaptions
          .map(
            (caption, index) => `
              <article class="recent-post-card">
                <div class="recent-post-meta">
                  <span>Post ${index + 1}</span>
                </div>

                <p>${escapeHtml(caption)}</p>
              </article>
            `
          )
          .join("")}
      </div>
    `
    : `
      <p class="detail-empty">
        No posts in the last 30 days.
      </p>
    `;

  els.drawerContent.innerHTML = `
    <section class="detail-section">
      <h3>Key information</h3>

      <dl class="detail-grid">
        <dt>Headline</dt>
        <dd>${escapeHtml(profile.headline || "—")}</dd>

        <dt>Location</dt>
        <dd>${escapeHtml(profile.location || "—")}</dd>

        <dt>Followers</dt>
        <dd>
          ${escapeHtml(profile.followers_count_text || "—")}
        </dd>

        <dt>Connections</dt>
        <dd>
          ${escapeHtml(profile.connections_count_text || "—")}
        </dd>

        <dt>Posts</dt>
        <dd>${postCaptions.length}</dd>

        <dt>Last scan</dt>
        <dd>${escapeHtml(formatDate(profile.scraped_at))}</dd>
      </dl>
    </section>

    <section class="detail-section">
      <h3>LinkedIn</h3>
      ${linkedInBlock}
    </section>

    <section class="detail-section">
      <h3>About</h3>

      <p class="detail-pre">
        ${escapeHtml(
          profile.about_text ||
          "No About data."
        )}
      </p>
    </section>

    <section class="detail-section">
      <div class="detail-section-heading">
        <h3>Recent posts</h3>

        <span class="detail-count">
          ${postCaptions.length}
        </span>
      </div>

      ${recentPostsBlock}
    </section>

    <section class="detail-section">
      <h3>Experience</h3>

      <p class="detail-pre">
        ${escapeHtml(
          profile.experience_raw_text ||
          "No Experience data."
        )}
      </p>
    </section>
  `;

  els.drawerBackdrop.hidden = false;
  els.detailDrawer.classList.add("is-open");
  els.detailDrawer.setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";
}

function closeDrawer() {
  els.drawerBackdrop.hidden = true;
  els.detailDrawer.classList.remove("is-open");
  els.detailDrawer.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
}


function renderOutreachReplyInbox() {
  const replies = Array.isArray(state.outreachReplies) ? state.outreachReplies : [];
  const configured = Array.isArray(state.outreachReplyAccounts)
    ? state.outreachReplyAccounts : [];
  const replyCounts = new Map(configured.map((account) => [
    String(account.account_id || "").trim(), Number(account.reply_count || 0)
  ]));
  const accountMap = new Map(configured.map((account) => [
    String(account.account_id || "").trim(),
    String(account.display_name || account.account_id || "Outreach account").trim()
  ]));
  replies.forEach((reply) => {
    const id = String(reply.assigned_account_id || "").trim();
    if (id && !accountMap.has(id)) accountMap.set(id, getOutreachAccountDisplayName(id));
  });
  const accounts = Array.from(accountMap, ([id, name]) => ({ id, name }));
  if (!accountMap.has(state.outreachReplySelectedAccountId)) {
    state.outreachReplySelectedAccountId = accounts.find((account) =>
      replies.some((reply) => String(reply.assigned_account_id || "").trim() === account.id)
    )?.id || accounts[0]?.id || null;
  }
  if (els.outreachReplyTabCount) els.outreachReplyTabCount.textContent =
    String(Array.from(replyCounts.values()).reduce((total, count) => total + count, 0));
  els.outreachReplyAccountTabs?.replaceChildren();
  accounts.forEach((account) => {
    const count = replyCounts.get(account.id) ?? replies.filter((reply) =>
      String(reply.assigned_account_id || "").trim() === account.id
    ).length;
    const button = document.createElement("button");
    button.type = "button";
    button.className = "outreach-reply-account-tab";
    button.classList.toggle("is-active", account.id === state.outreachReplySelectedAccountId);
    button.setAttribute("role", "tab");
    button.setAttribute("aria-selected", String(account.id === state.outreachReplySelectedAccountId));
    button.innerHTML = `<strong>${escapeHtml(account.name)}</strong><span>${count}</span>`;
    button.addEventListener("click", () => {
      state.outreachReplySelectedAccountId = account.id;
      renderOutreachReplies();
      if (!state.outreachReplyLoadedByAccount[account.id] ||
          state.outreachReplyLoadErrorByAccount[account.id]) {
        void loadMoreOutreachReplies(account.id);
      }
    });
    els.outreachReplyAccountTabs?.appendChild(button);
  });

  if (!els.outreachReplyList || !els.outreachReplyConversation || !els.outreachReplyInbox) return;
  const previousListAccount = els.outreachReplyList.dataset.accountId;
  if (previousListAccount) {
    state.outreachReplyScrollByAccount[previousListAccount] = els.outreachReplyList.scrollTop;
  }
  els.outreachReplyList.replaceChildren();
  els.outreachReplyConversation.replaceChildren();
  if (state.outreachRepliesLoading) {
    els.outreachReplyEmpty.hidden = false;
    els.outreachReplyEmpty.textContent = "Loading verified replies...";
    els.outreachReplyInbox.hidden = true;
    return;
  }
  const accountId = state.outreachReplySelectedAccountId;
  els.outreachReplyList.dataset.accountId = accountId || "";
  const accountReplies = replies.filter((reply) =>
    String(reply.assigned_account_id || "").trim() === accountId
  );
  if (!accountReplies.length) {
    const loadError = state.outreachReplyLoadErrorByAccount[accountId];
    els.outreachReplyEmpty.hidden = false;
    els.outreachReplyEmpty.textContent = loadError
      ? `Could not load conversations: ${loadError}`
      : !state.outreachReplyLoadedByAccount[accountId]
        ? "Loading conversations..."
        : accounts.length
          ? "No verified replies have been captured for this account yet."
          : "No verified replies have been captured yet.";
    els.outreachReplyInbox.hidden = true;
    return;
  }
  els.outreachReplyEmpty.hidden = true;
  els.outreachReplyInbox.hidden = false;
  if (els.outreachReplyAccountCount) els.outreachReplyAccountCount.textContent =
    String(replyCounts.get(accountId) ?? accountReplies.length);

  const visibleReplies = accountReplies;

  const selectedIds = state.outreachReplySelectedIdByAccount;
  if (!visibleReplies.some((reply) => String(reply.id) === selectedIds[accountId])) {
    selectedIds[accountId] = String(visibleReplies[0]?.id || "");
  }
  visibleReplies.forEach((reply) => {
    const id = String(reply.id || "");
    const name = String(reply.user_name || "LinkedIn user").trim();
    const text = String(reply.message_text || "No message content captured.").trim();
    const campaignName = String(reply.campaign_name || "").trim();
    const sourceBatch = String(reply.connect_batch_code || reply.connect_batch_id || "").trim();
    const sourceLabel = String(reply.connect_batch_label || "").trim() ||
      `Campaign: ${campaignName || "Unavailable"} · Batch ID: ${sourceBatch || "Unavailable"}`;
    const row = document.createElement("button");
    row.type = "button";
    row.className = "reply-inbox-person";
    row.classList.toggle("is-active", id === selectedIds[accountId]);
    row.setAttribute("aria-current", id === selectedIds[accountId] ? "true" : "false");
    row.innerHTML = `<span class="reply-inbox-avatar" aria-hidden="true">${escapeHtml(name.charAt(0).toUpperCase())}</span>
      <span class="reply-inbox-person-copy"><strong>${escapeHtml(name)}</strong><small>${escapeHtml(text)}</small><span class="reply-inbox-person-source" title="${escapeHtml(sourceLabel)}">${escapeHtml(sourceLabel)}</span></span>
      <span class="reply-inbox-person-date">${escapeHtml(reply.captured_at ? formatDate(reply.captured_at) : "")}</span>`;
    row.addEventListener("click", () => {
      selectedIds[accountId] = id;
      renderOutreachReplies();
    });
    els.outreachReplyList.appendChild(row);
  });
  const loadingMore = state.outreachReplyLoadingMoreByAccount[accountId];
  const loadError = state.outreachReplyLoadErrorByAccount[accountId];
  if (loadingMore || loadError || state.outreachReplyHasMoreByAccount[accountId]) {
    const status = document.createElement("div");
    status.className = "reply-inbox-load-state";
    if (loadError) {
      status.textContent = "Could not load more contacts. ";
      const retry = document.createElement("button");
      retry.type = "button";
      retry.textContent = "Try again";
      retry.addEventListener("click", () => void loadMoreOutreachReplies(accountId));
      status.appendChild(retry);
    } else {
      status.textContent = loadingMore ? "Loading more contacts…" : "Scroll for more contacts";
    }
    els.outreachReplyList.appendChild(status);
  }
  els.outreachReplyList.scrollTop = state.outreachReplyScrollByAccount[accountId] || 0;

  const reply = visibleReplies.find((item) => String(item.id) === selectedIds[accountId]);
  if (!reply) return;
  const id = String(reply.id || "");
  const name = String(reply.user_name || "LinkedIn user").trim();
  const accountName = accountMap.get(accountId) || accountId;
  const batch = String(reply.message_batch_code || "").trim();
  const campaignName = String(reply.campaign_name || "").trim();
  const sourceBatchCode = String(reply.connect_batch_code || "").trim();
  const sourceBatchId = String(reply.connect_batch_id || "").trim();
  const sourceBatchLabel = String(reply.connect_batch_label || "").trim() || sourceBatchCode || sourceBatchId;
  const rawUrl = String(reply.linkedin_url || "").trim();
  let safeUrl = "";
  try {
    const url = new URL(rawUrl);
    if (["https:", "http:"].includes(url.protocol)) safeUrl = url.href;
  } catch (error) { /* No navigable LinkedIn URL. */ }
  const sourceMessages = Array.isArray(reply.conversation_messages) ? reply.conversation_messages : [];
  const sameParticipant = (left, right) => {
    const tokens = (value) => String(value || "").normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase().trim().split(/\s+/).filter(Boolean).sort();
    const leftTokens = tokens(left);
    const rightTokens = tokens(right);
    return leftTokens.length > 0 && leftTokens.length === rightTokens.length &&
      leftTokens.every((token, index) => token === rightTokens[index]);
  };
  const messages = [...sourceMessages];
  if (!messages.length && reply.message_text) {
    messages.push({ text: reply.message_text, is_own_message: false, timestamp: reply.linkedin_message_time || "" });
  }
  const job = reply.send_job && typeof reply.send_job === "object" ? reply.send_job : null;
  const status = String(job?.status || "").toLowerCase();
  const locked = state.outreachReplySendSubmitting || status === "queued" || status === "processing";
  const hasProfileUrl = /^https?:\/\/(?:[a-z]{2}\.)?(?:www\.)?linkedin\.com\/in\/[^/?#]+\/?(?:[?#].*)?$/i.test(rawUrl);
  const header = `<header class="reply-inbox-chat-header">
    <span class="reply-inbox-avatar is-large" aria-hidden="true">${escapeHtml(name.charAt(0).toUpperCase())}</span>
    <div class="reply-inbox-chat-identity"><h3>${escapeHtml(name)}</h3><p>${escapeHtml(accountName)}${batch ? ` · Message batch ${escapeHtml(batch)}` : ""}</p>
      <p class="reply-inbox-chat-source" title="${sourceBatchId ? `Source Connect batch ID: ${escapeHtml(sourceBatchId)}` : "Source Connect batch unavailable"}">${escapeHtml(sourceBatchLabel || `Campaign: ${campaignName || "Unavailable"}`)}</p></div>
    ${safeUrl ? `<a href="${escapeHtml(safeUrl)}" target="_blank" rel="noopener noreferrer" class="reply-inbox-link">LinkedIn ↗</a>` : ""}
  </header>`;
  const conversation = messages.length ? messages.map((message) => {
    const direction = message.sender_type || (message.is_own_message || sameParticipant(message.author, accountName)
      ? "own" : message.is_incoming || sameParticipant(message.author, name) ? "incoming" : "unknown");
    const senderName = direction === "own" ? accountName : direction === "incoming" ? name : "Sender unverified";
    return `
    <article class="reply-inbox-message ${direction === "own" ? "is-own" : direction === "incoming" ? "is-incoming" : "is-unknown"}">
      <span class="reply-inbox-message-author">${escapeHtml(senderName)}</span>
      <div class="reply-inbox-bubble">${escapeHtml(message.text || "")}</div>
      <time>${escapeHtml(message.timestamp || "")}</time>
    </article>`;
  }).join("") : `<p class="reply-inbox-no-history">No conversation history captured yet.</p>`;
  els.outreachReplyConversation.innerHTML = `${header}
    <div class="reply-inbox-thread">${conversation}</div>
    <div class="reply-inbox-compose">
      ${job ? `<p class="reply-inbox-job-status">Worker status: ${escapeHtml(status)}${job.last_error ? ` · ${escapeHtml(job.last_error)}` : ""}</p>` : ""}
      <div class="reply-inbox-compose-field">
        <textarea id="outreachReplyInlineInput" rows="3" aria-label="Reply message" placeholder="Message..."></textarea>
        <button id="outreachReplyInlineSend" type="button" ${locked || !hasProfileUrl ? "disabled" : ""} aria-label="Send via worker" title="${hasProfileUrl ? "" : "A verified profile link is required before sending"}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m3 11 18-8-8 18-2.5-7.5L3 11Z"/><path d="M10.5 13.5 21 3"/></svg><span>${state.outreachReplySendSubmitting ? "Sending..." : "Send via worker"}</span></button>
      </div>
      <p id="outreachReplyInlineError" class="reply-inbox-inline-error" ${state.outreachReplySendErrors[id] ? "" : "hidden"}>${escapeHtml(state.outreachReplySendErrors[id] || "")}</p>
    </div>`;
  const input = els.outreachReplyConversation.querySelector("#outreachReplyInlineInput");
  input.value = Object.prototype.hasOwnProperty.call(state.outreachReplyDrafts, id)
    ? state.outreachReplyDrafts[id] : String(job?.message_text || "");
  input.addEventListener("input", () => { state.outreachReplyDrafts[id] = input.value; });
  els.outreachReplyConversation.querySelector("#outreachReplyInlineSend")?.addEventListener("click", async () => {
    const messageText = input.value.trim();
    const errorEl = els.outreachReplyConversation.querySelector("#outreachReplyInlineError");
    if (!messageText) {
      errorEl.textContent = "Enter a message before sending.";
      errorEl.hidden = false;
      input.focus();
      return;
    }
    if (!window.confirm(`Send this reply to ${name} via the LinkedIn worker?`)) return;
    delete state.outreachReplySendErrors[id];
    state.outreachReplySendSubmitting = true;
    renderOutreachReplies();
    try {
      const response = await fetch(`/api/outreach/replies/${encodeURIComponent(id)}/send`, {
        method: "POST", headers: { "Accept": "application/json", "Content-Type": "application/json" },
        body: JSON.stringify({ message_text: messageText })
      });
      const result = await response.json();
      if (!response.ok || !result.ok) throw new Error(result.error || "Could not queue the reply message.");
      reply.send_job = result.job;
      delete state.outreachReplyDrafts[id];
    } catch (error) {
      state.outreachReplyDrafts[id] = messageText;
      state.outreachReplySendErrors[id] = error.message || String(error);
    } finally {
      state.outreachReplySendSubmitting = false;
      renderOutreachReplies();
    }
  });
  els.outreachReplyConversation.querySelector(".reply-inbox-thread")?.scrollTo({ top: 999999 });
  requestAnimationFrame(maybeLoadMoreOutreachReplies);
}

function renderOutreachReplies() {
  renderOutreachReplyInbox();
}

const OUTREACH_REPLY_BATCH_SIZE = 20;

function outreachReplyContactKey(reply) {
  const account = String(reply.assigned_account_id || "").trim().toLowerCase();
  const identity = String(reply.linkedin_url || reply.user_name || reply.id || "").trim().toLowerCase();
  return `${account}|${identity}`;
}

function maybeLoadMoreOutreachReplies() {
  if (document.querySelector("#tab-replies")?.hidden || els.outreachReplyInbox?.hidden) return;
  const accountId = state.outreachReplySelectedAccountId;
  const list = els.outreachReplyList;
  if (!accountId || !list || !state.outreachReplyHasMoreByAccount[accountId] ||
      state.outreachReplyLoadingMoreByAccount[accountId] ||
      state.outreachReplyLoadErrorByAccount[accountId]) return;
  if (list.scrollHeight - list.scrollTop - list.clientHeight < 180) {
    void loadMoreOutreachReplies(accountId);
  }
}

async function loadMoreOutreachReplies(accountId) {
  if (!accountId || state.outreachReplyLoadingMoreByAccount[accountId] ||
      state.outreachReplyHasMoreByAccount[accountId] === false) return;
  const generation = state.outreachReplyRequestGeneration;
  const offset = Number(state.outreachReplyNextOffsetByAccount[accountId] || 0);
  state.outreachReplyLoadingMoreByAccount[accountId] = true;
  delete state.outreachReplyLoadErrorByAccount[accountId];
  renderOutreachReplies();
  try {
    const params = new URLSearchParams({
      account_id: accountId, offset: String(offset), limit: String(OUTREACH_REPLY_BATCH_SIZE)
    });
    const response = await fetch(`/api/outreach/replies?${params}`, {
      headers: { "Accept": "application/json" }, cache: "no-store"
    });
    const result = await response.json();
    if (!response.ok || !result.ok) {
      throw new Error(result.detail || result.error || "Could not load more contacts.");
    }
    if (generation !== state.outreachReplyRequestGeneration) return;
    const page = Array.isArray(result.replies) ? result.replies : [];
    const seen = new Set(state.outreachReplies.map(outreachReplyContactKey));
    for (const reply of page) {
      const key = outreachReplyContactKey(reply);
      if (!seen.has(key)) {
        seen.add(key);
        state.outreachReplies.push(reply);
      }
    }
    state.outreachReplyNextOffsetByAccount[accountId] = Number(result.next_offset) || offset + page.length;
    state.outreachReplyHasMoreByAccount[accountId] = Boolean(result.has_more && page.length);
    state.outreachReplyLoadedByAccount[accountId] = true;
  } catch (error) {
    if (generation !== state.outreachReplyRequestGeneration) return;
    state.outreachReplyLoadErrorByAccount[accountId] = error.message || String(error);
  } finally {
    if (generation === state.outreachReplyRequestGeneration) {
      state.outreachReplyLoadingMoreByAccount[accountId] = false;
      renderOutreachReplies();
    }
  }
}

els.outreachReplyList?.addEventListener("scroll", () => {
  const accountId = els.outreachReplyList.dataset.accountId;
  if (accountId) state.outreachReplyScrollByAccount[accountId] = els.outreachReplyList.scrollTop;
  maybeLoadMoreOutreachReplies();
}, { passive: true });

async function loadOutreachReplies() {
  void pollLatestOutreachReplyScan();
  if (state.outreachRepliesLoading) {
    return;
  }

  state.outreachRepliesLoading = true;
  const generation = ++state.outreachReplyRequestGeneration;
  if (els.outreachReplyError) {
    els.outreachReplyError.hidden = true;
    els.outreachReplyError.textContent = "";
  }
  renderOutreachReplies();

  try {
    const response = await fetch(
      "/api/outreach/replies?metadata=1",
      {
        method: "GET",
        headers: { "Accept": "application/json" },
        cache: "no-store"
      }
    );
    const result = await response.json();

    if (!response.ok || !result.ok) {
      throw new Error(
        result.detail || result.error || "Could not load Outreach replies."
      );
    }

    if (generation !== state.outreachReplyRequestGeneration) return;
    state.outreachReplies = [];
    state.outreachReplyRevision = result.revision ?? null;
    state.outreachReplyAccounts = Array.isArray(result.accounts)
      ? result.accounts
      : [];
    state.outreachReplyNextOffsetByAccount = {};
    state.outreachReplyHasMoreByAccount = {};
    state.outreachReplyLoadedByAccount = {};
    state.outreachReplyLoadingMoreByAccount = {};
    state.outreachReplyLoadErrorByAccount = {};
    state.outreachReplyScrollByAccount = {};
    for (const account of state.outreachReplyAccounts) {
      const id = String(account.account_id || "").trim();
      const count = Number(account.reply_count || 0);
      state.outreachReplyHasMoreByAccount[id] = count > 0;
      state.outreachReplyLoadedByAccount[id] = count === 0;
    }
    const previousId = state.outreachReplySelectedAccountId;
    if (!state.outreachReplyAccounts.some((account) => account.account_id === previousId && account.reply_count > 0)) {
      state.outreachReplySelectedAccountId = state.outreachReplyAccounts.find((account) => account.reply_count > 0)?.account_id ||
        state.outreachReplyAccounts[0]?.account_id || null;
    }
  } catch (error) {
    state.outreachReplies = [];
    if (els.outreachReplyError) {
      els.outreachReplyError.textContent = error.message || String(error);
      els.outreachReplyError.hidden = false;
    }
  } finally {
    state.outreachRepliesLoading = false;
    renderOutreachReplies();
  }
  const accountId = state.outreachReplySelectedAccountId;
  if (accountId && state.outreachReplyHasMoreByAccount[accountId]) {
    await loadMoreOutreachReplies(accountId);
  }
}

async function reloadOutreachRepliesAfterScan() {
  // A periodic/manual load may still be in flight when the worker completes.
  // Wait for it to release the loading guard, then fetch the completed scan's
  // metadata and selected account page instead of silently dropping refresh.
  while (state.outreachRepliesLoading) {
    await new Promise((resolve) => window.setTimeout(resolve, 100));
  }
  await loadOutreachReplies();
}

async function refreshOutreachRepliesAfterScan() {
  if (state.outreachReplyRefreshing || state.outreachRepliesLoading ||
      state.outreachReplySendSubmitting) return;
  state.outreachReplyRefreshing = true;
  const accountId = state.outreachReplySelectedAccountId;
  const previousAccount = state.outreachReplyAccounts.find(
    (account) => account.account_id === accountId
  );
  const previousCount = Number(previousAccount?.reply_count || 0);
  const previouslyLoaded = Number(state.outreachReplyNextOffsetByAccount[accountId] || 0);
  const selectedId = state.outreachReplySelectedIdByAccount[accountId];
  const inputFocused = document.activeElement?.id === "outreachReplyInlineInput";
  const inputSelection = inputFocused ? [document.activeElement.selectionStart, document.activeElement.selectionEnd] : null;

  try {
    const metadataResponse = await fetch("/api/outreach/replies?metadata=1", { cache: "no-store" });
    const metadata = await metadataResponse.json();
    if (!metadataResponse.ok || !metadata.ok) throw new Error(metadata.error || "Could not refresh replies.");
    const accounts = Array.isArray(metadata.accounts) ? metadata.accounts : [];
    const nextCount = Number(accounts.find((account) => account.account_id === accountId)?.reply_count || 0);
    const targetCount = Math.max(OUTREACH_REPLY_BATCH_SIZE,
      previouslyLoaded + Math.max(0, nextCount - previousCount));
    const refreshed = [];
    let hasMore = false;
    if (accountId && nextCount > 0) {
      while (refreshed.length < targetCount) {
        const params = new URLSearchParams({
          account_id: accountId,
          offset: String(refreshed.length),
          limit: String(Math.min(50, targetCount - refreshed.length))
        });
        const response = await fetch(`/api/outreach/replies?${params}`, { cache: "no-store" });
        const page = await response.json();
        if (!response.ok || !page.ok) throw new Error(page.error || "Could not refresh conversations.");
        const rows = Array.isArray(page.replies) ? page.replies : [];
        refreshed.push(...rows);
        hasMore = Boolean(page.has_more);
        if (!rows.length || !hasMore) break;
      }
    }
    if (document.querySelector("#tab-replies")?.hidden ||
        accountId !== state.outreachReplySelectedAccountId) return;

    ++state.outreachReplyRequestGeneration;
    state.outreachReplyAccounts = accounts;
    state.outreachReplies = refreshed;
    state.outreachReplyNextOffsetByAccount = { [accountId]: refreshed.length };
    state.outreachReplyHasMoreByAccount = { [accountId]: hasMore };
    state.outreachReplyLoadedByAccount = { [accountId]: true };
    state.outreachReplyLoadingMoreByAccount = {};
    state.outreachReplyLoadErrorByAccount = {};
    state.outreachReplyRevision = metadata.revision ?? null;
    renderOutreachReplies();
    if (inputFocused && selectedId === state.outreachReplySelectedIdByAccount[accountId]) {
      const input = els.outreachReplyConversation?.querySelector("#outreachReplyInlineInput");
      if (input) {
        input.focus();
        if (inputSelection.every(Number.isInteger)) input.setSelectionRange(...inputSelection);
      }
    }
  } catch (error) {
    console.error("Reply refresh error:", error);
  } finally {
    state.outreachReplyRefreshing = false;
  }
}

async function pollOutreachReplyRevision() {
  if (document.hidden || document.querySelector("#tab-replies")?.hidden ||
      state.outreachRepliesLoading || state.outreachReplyRevisionLoading ||
      state.outreachReplyRefreshing || state.outreachReplySendSubmitting) return;
  state.outreachReplyRevisionLoading = true;
  try {
    const response = await fetch("/api/outreach/replies?revision_only=1", { cache: "no-store" });
    const result = await response.json();
    if (!response.ok || !result.ok) throw new Error(result.error || "Could not check replies.");
    if ((result.revision ?? null) !== state.outreachReplyRevision) {
      await refreshOutreachRepliesAfterScan();
    }
  } catch (error) {
    console.error("Reply revision error:", error);
  } finally {
    state.outreachReplyRevisionLoading = false;
  }
}

function formatOutreachReplyScanTime(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Last scan: —";
  const formatted = new Intl.DateTimeFormat("en-GB", {
    day: "numeric", month: "short", hour: "numeric", minute: "2-digit"
  }).format(date);
  return `Last scanned ${formatted}`;
}

async function pollLatestOutreachReplyScan() {
  if (document.hidden || document.querySelector("#tab-replies")?.hidden ||
      state.outreachReplyLastScanLoading) return;
  state.outreachReplyLastScanLoading = true;
  try {
    const response = await fetch("/api/outreach/reply-check/latest", { cache: "no-store" });
    const result = await response.json();
    if (!response.ok || !result.ok) throw new Error(result.error || "Could not load last scan time.");
    const scan = result.last_scan;
    const scanId = scan?.id || null;
    const changed = state.outreachReplyLastScanInitialized && scanId &&
      scanId !== state.outreachReplyLastScanId;
    state.outreachReplyLastScanId = scanId;
    state.outreachReplyLastScanInitialized = true;
    const button = document.querySelector("#outreachReplyCheckButton");
    const lastScan = document.querySelector("#outreachReplyLastScan");
    if (lastScan) {
      const label = scan ? formatOutreachReplyScanTime(scan.finished_at) : "Last scan: —";
      if (lastScan.textContent !== label) lastScan.textContent = label;
      lastScan.title = scan?.finished_at ? new Date(scan.finished_at).toLocaleString() : "";
    }
    if (changed && !button?.disabled) await refreshOutreachRepliesAfterScan();
  } catch (error) {
    console.error("Last reply scan error:", error);
  } finally {
    state.outreachReplyLastScanLoading = false;
  }
}

async function requestOutreachReplyCheck() {
  const button = document.querySelector("#outreachReplyCheckButton");
  const status = document.querySelector("#outreachReplyCheckStatus");
  if (!button || button.disabled) return;
  button.disabled = true;
  button.textContent = "Queueing…";
  status.textContent = "Sending request to worker…";
  try {
    const response = await fetch("/api/outreach/reply-check", { method: "POST" });
    const result = await response.json();
    if (!response.ok || !result.ok) throw new Error(result.error || "Could not queue reply check.");
    const requestId = result.request?.id;
    if (!requestId) throw new Error("Worker request was queued without an ID.");
    status.textContent = result.request.already_active
      ? "A reply check is already queued or running."
      : "Queued — waiting for worker…";
    button.textContent = "Check queued";
    while (true) {
      await new Promise((resolve) => window.setTimeout(resolve, 4000));
      const checkResponse = await fetch(`/api/outreach/reply-check/${encodeURIComponent(requestId)}`, { cache: "no-store" });
      const checkResult = await checkResponse.json();
      if (!checkResponse.ok || !checkResult.ok) throw new Error(checkResult.error || "Could not get reply-check status.");
      const request = checkResult.request;
      if (request.status === "running") {
        button.textContent = "Checking…";
        status.textContent = "Worker is checking all accounts…";
      } else if (request.status === "completed") {
        button.textContent = "Check replies";
        status.textContent = "";
        const lastScan = document.querySelector("#outreachReplyLastScan");
        if (lastScan) lastScan.textContent = formatOutreachReplyScanTime(request.finished_at);
        state.outreachReplyLastScanId = request.id;
        state.outreachReplyLastScanInitialized = true;
        await reloadOutreachRepliesAfterScan();
        break;
      } else if (request.status === "failed") {
        throw new Error(request.error || "Worker could not complete the reply check.");
      }
    }
  } catch (error) {
    status.textContent = error.message || String(error);
  } finally {
    button.disabled = false;
    if (button.textContent !== "Check replies") button.textContent = "Check replies";
  }
}

function renderCampaignPerformanceFilter() {
  const select = document.querySelector("#campaignPerformanceFilter");
  if (!select) return;
  const campaigns = state.campaignPerformanceOptions.length
    ? state.campaignPerformanceOptions : state.campaignPerformance;
  select.replaceChildren(new Option("All campaigns", "all"));
  [...campaigns]
    .sort((left, right) => String(left.campaign_name).localeCompare(String(right.campaign_name)))
    .forEach((campaign) => select.add(new Option(campaign.campaign_name, campaign.campaign_id)));
  if (!campaigns.some((campaign) => campaign.campaign_id === state.campaignPerformanceFilter)) {
    state.campaignPerformanceFilter = "all";
  }
  select.value = state.campaignPerformanceFilter;
  renderConnectDropdown(connectDropdowns[3]);
}

function renderCampaignPerformance() {
  const status = document.querySelector("#campaignsStatus");
  const table = document.querySelector("#campaignsTable");
  const rows = document.querySelector("#campaignsRows");
  if (!status || !table || !rows) return;
  document.querySelectorAll("[data-campaign-window]").forEach((button) => {
    const active = button.dataset.campaignWindow === state.campaignPerformanceWindow;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-pressed", String(active));
  });
  status.classList.remove("is-error", "is-loading");
  if (state.campaignPerformanceLoading) {
    status.hidden = false;
    status.classList.add("is-loading");
    status.textContent = "Loading campaign performance…";
    table.hidden = true;
    return;
  }
  const campaigns = state.campaignPerformanceFilter === "all"
    ? state.campaignPerformance
    : state.campaignPerformance.filter((campaign) =>
        campaign.campaign_id === state.campaignPerformanceFilter);
  if (state.campaignPerformanceError) {
    status.hidden = false;
    status.classList.add("is-error");
    status.innerHTML = `<span>${escapeHtml(state.campaignPerformanceError)}</span><button type="button" data-campaign-retry>Try again</button>`;
    table.hidden = true;
    return;
  }
  status.hidden = campaigns.length > 0;
  table.hidden = campaigns.length === 0;
  if (!campaigns.length) status.textContent = state.campaignPerformanceFilter === "all"
    ? "No Connect batches in this timeframe."
    : "No batches for this campaign in this timeframe.";
  rows.innerHTML = campaigns.map((campaign) => {
    const id = String(campaign.campaign_id || "");
    const expanded = id === state.expandedCampaignId;
    const batches = Array.isArray(campaign.batches) ? campaign.batches : [];
    const accounts = Array.isArray(campaign.accounts) ? campaign.accounts : [];
    const codes = batches.map((batch) => String(batch.batch_label || batch.batch_code || batch.batch_id || ""));
    const summary = codes.length <= 2 ? codes.join(", ") : `${codes[0]} + ${codes.length - 1} more`;
    const detail = expanded ? `<div class="campaigns-detail">
      <section class="campaigns-detail-section"><h3>By Connect batch</h3><div class="campaigns-detail-head"><span>Batch</span><span>Created</span><span>Added</span><span>Messaged</span><span>Replies</span><span>Reply rate</span></div>${batches.map((batch) => `
        <div class="campaigns-batch-row"><strong title="Batch ID: ${escapeHtml(batch.batch_code || batch.batch_id || "")}">${escapeHtml(batch.batch_label || batch.batch_code || batch.batch_id)}</strong><span>${escapeHtml(formatDate(batch.created_at))}</span><span>${Number(batch.added || 0)}</span><span>${Number(batch.messaged || 0)}</span><span>${Number(batch.replies || 0)}</span><span>${Number(batch.reply_rate || 0).toFixed(1)}%</span></div>`).join("")}</section>
      <section class="campaigns-detail-section"><div class="campaigns-detail-head"><span>Account</span><span>Account ID</span><span>Added</span><span>Messaged</span><span>Replies</span><span>Reply rate</span></div>${accounts.length ? accounts.map((account) => `
        <div class="campaigns-batch-row"><strong>${escapeHtml(account.account_id === "unassigned" ? "Unassigned" : getOutreachAccountDisplayName(account.account_id))}</strong><span>${escapeHtml(account.account_id === "unassigned" ? "—" : account.account_id)}</span><span>${Number(account.added || 0)}</span><span>${Number(account.messaged || 0)}</span><span>${Number(account.replies || 0)}</span><span>${Number(account.reply_rate || 0).toFixed(1)}%</span></div>`).join("") : '<p class="campaigns-detail-empty">No account data for these batches.</p>'}</section>
    </div>` : "";
    return `<button type="button" class="campaigns-row" data-campaign-id="${escapeHtml(id)}" aria-expanded="${expanded}" aria-label="${escapeHtml(campaign.campaign_name)}: ${codes.length} batches, ${campaign.replies} replies. ${expanded ? "Hide" : "Show"} details">
      <strong>${escapeHtml(campaign.campaign_name)}</strong><span class="campaigns-batch-summary" title="${escapeHtml(codes.join("\n"))}">${escapeHtml(summary)}</span><span>${Number(campaign.added || 0)}</span><span>${Number(campaign.messaged || 0)}</span><span>${Number(campaign.replies || 0)}</span><span>${Number(campaign.reply_rate || 0).toFixed(1)}%</span></button>${detail}`;
  }).join("");
}

async function loadCampaignPerformance() {
  const requestId = ++state.campaignPerformanceRequestId;
  state.campaignPerformanceLoading = true;
  state.campaignPerformanceError = "";
  renderCampaignPerformance();
  try {
    const response = await fetch(`/api/outreach/campaigns/performance?window=${encodeURIComponent(state.campaignPerformanceWindow)}`, {cache: "no-store"});
    const result = await response.json();
    if (!response.ok || !result.ok) throw new Error(result.error || "Could not load campaigns.");
    if (requestId !== state.campaignPerformanceRequestId) return;
    state.campaignPerformance = Array.isArray(result.campaigns) ? result.campaigns : [];
    if (state.campaignPerformanceWindow === "all") {
      state.campaignPerformanceOptions = state.campaignPerformance;
    }
    renderCampaignPerformanceFilter();
    renderCampaignPerformance();
  } catch (error) {
    if (requestId !== state.campaignPerformanceRequestId) return;
    state.campaignPerformance = [];
    state.campaignPerformanceError = error.message || "Could not load campaigns.";
  } finally {
    if (requestId === state.campaignPerformanceRequestId) {
      state.campaignPerformanceLoading = false;
      renderCampaignPerformance();
    }
  }
}

document.querySelectorAll("[data-campaign-window]").forEach((button) => {
  button.addEventListener("click", () => {
    if (state.campaignPerformanceWindow === button.dataset.campaignWindow) return;
    state.campaignPerformanceWindow = button.dataset.campaignWindow;
    state.expandedCampaignId = null;
    void loadCampaignPerformance();
  });
});
document.querySelector("#campaignPerformanceFilter")?.addEventListener("change", (event) => {
  state.campaignPerformanceFilter = event.target.value;
  state.expandedCampaignId = null;
  renderCampaignPerformance();
});
document.querySelector("#campaignsRows")?.addEventListener("click", (event) => {
  const button = event.target.closest("[data-campaign-id]");
  if (!button) return;
  const campaignId = button.dataset.campaignId;
  state.expandedCampaignId = state.expandedCampaignId === campaignId
    ? null : campaignId;
  renderCampaignPerformance();
  Array.from(document.querySelectorAll("#campaignsRows [data-campaign-id]"))
    .find((row) => row.dataset.campaignId === campaignId)?.focus();
});
document.querySelector("#campaignsStatus")?.addEventListener("click", (event) => {
  if (event.target.closest("[data-campaign-retry]")) void loadCampaignPerformance();
});

function switchTab(tabName) {
  document
    .querySelectorAll(".tab-button")
    .forEach((button) => {
      const active = button.dataset.tab === tabName &&
          (tabName !== "outreach" ||
            button.dataset.outreachProcessTab === state.outreachProcessTab);
      button.classList.toggle("is-active", active);
      if (button.dataset.tab) {
        if (active) button.setAttribute("aria-current", "page");
        else button.removeAttribute("aria-current");
      }
    });

  document.querySelectorAll(".outreach-reply-tab").forEach((button) => {
    const active = tabName === "replies";
    button.classList.toggle("is-active", active);
    if (active) button.setAttribute("aria-current", "page");
    else button.removeAttribute("aria-current");
  });

  document.querySelectorAll("#outreachWorkflowNavigation [data-outreach-process-tab]")
    .forEach((button) => {
      const active = tabName === "outreach" &&
        button.dataset.outreachProcessTab === state.outreachProcessTab;
      button.classList.toggle("is-active", active);
      if (active) button.setAttribute("aria-current", "page");
      else button.removeAttribute("aria-current");
    });

  const workflowNavigation = document.querySelector("#outreachWorkflowNavigation");
  if (workflowNavigation) {
    workflowNavigation.hidden = tabName !== "outreach" && tabName !== "replies";
    requestAnimationFrame(syncOutreachWorkflowPill);
  }

  document
    .querySelectorAll(".tab-panel")
    .forEach((panel) => {
      panel.hidden =
        panel.id !== `tab-${tabName}`;
    });

  const mainScroll = document.querySelector("#appMainScroll");
  if (mainScroll) {
    mainScroll.scrollTop = 0;
    mainScroll.classList.toggle(
      "is-connect-workspace",
      tabName === "outreach" && state.outreachProcessTab === "connect"
    );
  }

  const pageCopy = {
    overview: {
      eyebrow: "Workspace",
      title: "Overview",
      subtitle: "Monitor system status, queues, workers, and recent activity."
    },
    profiles: {
      eyebrow: "Scanner",
      title: "Profiles",
      subtitle: "LinkedIn profile snapshots collected and stored in the database."
    },
    queue: {
      eyebrow: "Scanner",
      title: "Processing Queue",
      subtitle: "Monitor waiting URLs, active work, and scan history."
    },
    accounts: {
      eyebrow: "Infrastructure",
      title: "Accounts",
      subtitle: "Status of the LinkedIn browser profiles serving the scanner."
    },
    youtube: {
      eyebrow: "Research",
      title: "YouTube Research",
      subtitle: "Create research jobs and track channel results in real time."
    },
    outreach: {
      eyebrow: "Outreach",
      title: {
        connect: "Connect",
        acceptance: "Acceptance",
        recipients: "Recipients",
        messages: "Messages"
      }[state.outreachProcessTab] || "Connect",
      subtitle: {
        connect: "Send connection requests to LinkedIn profiles.",
        acceptance: "Check which connections were accepted.",
        recipients: "Prepare the people you want to message.",
        messages: "Create and follow up on your messages."
      }[state.outreachProcessTab] || "Send connection requests to LinkedIn profiles."
    },
    replies: {
      eyebrow: "Outreach",
      title: "Message Replies",
      subtitle: "Review verified LinkedIn replies captured by the Reply Check Worker."
    },
    campaigns: {
      eyebrow: "Outreach",
      title: "Campaigns",
      subtitle: "Compare performance across batches in each campaign."
    }
  };

  const copy =
    pageCopy[tabName] ||
    pageCopy.overview;

  if (els.pageEyebrow) {
    els.pageEyebrow.textContent = copy.eyebrow;
  }

  if (els.pageTitle) {
    els.pageTitle.textContent = copy.title;
  }

  if (els.pageSubtitle) {
    els.pageSubtitle.textContent = copy.subtitle;
  }
}


document
  .querySelectorAll(".tab-button")
  .forEach((button) => {
    button.addEventListener("click", () => {
      const tabName = button.dataset.tab;

      if (!tabName) {
        return;
      }

      switchTab(tabName);

      if (button.dataset.outreachProcessTab) {
        setOutreachProcessTab(button.dataset.outreachProcessTab);
      }

      const uiSettings = loadUiSettings();

      if (uiSettings.rememberLastSection) {
        localStorage.setItem(
          LAST_TAB_STORAGE_KEY,
          tabName
        );
      }

      if (button.dataset.tab === "profiles") {
        void loadOutreachProfiles();
      }

      if (button.dataset.tab === "replies") {
        void loadOutreachReplies();
      }
      if (button.dataset.tab === "campaigns") {
        void loadCampaignPerformance();
      }
    });
  });

els.killProcessButton?.addEventListener(
  "click",
  async () => {
    try {
      await sendWorkerCommand("kill_current");
    } catch (error) {
      window.alert(error.message || String(error));
    }
  }
);

els.stopScanButton?.addEventListener(
  "click",
  async () => {
    try {
      const command =
        normaliseStatus(state.worker?.status) === "paused"
          ? "resume_scan"
          : "stop_scan";

      await sendWorkerCommand(command);
    } catch (error) {
      window.alert(error.message || String(error));
    }
  }
);

function syncOutreachWorkflowPill() {
  document.querySelectorAll(".outreach-workflow-tabs").forEach((navigation) => {
    const active = navigation.querySelector(
      ".outreach-workflow-tab.is-active"
    );

    if (!navigation.offsetWidth || !active) return;

    navigation.style.setProperty(
      "--workflow-pill-left",
      `${active.offsetLeft}px`
    );
    navigation.style.setProperty(
      "--workflow-pill-width",
      `${active.offsetWidth}px`
    );
  });
}

const outreachWorkflowNavs = document.querySelectorAll(
  ".outreach-workflow-tabs"
);

if (outreachWorkflowNavs.length && "ResizeObserver" in window) {
  const workflowNavObserver = new ResizeObserver(syncOutreachWorkflowPill);
  outreachWorkflowNavs.forEach((navigation) => workflowNavObserver.observe(navigation));
}

window.addEventListener("resize", syncOutreachWorkflowPill);

const draggableWorkflowNavigation = document.querySelector("#outreachWorkflowNavigation");
const workflowNavPositionKey = "outreach-workflow-nav-position";

function clampWorkflowNavPosition(left, top) {
  const nav = draggableWorkflowNavigation;
  if (!nav) return;
  const margin = 8;
  const clampedLeft = Math.min(
    Math.max(margin, left),
    Math.max(margin, window.innerWidth - nav.offsetWidth - margin)
  );
  const clampedTop = Math.min(
    Math.max(margin, top),
    Math.max(margin, window.innerHeight - nav.offsetHeight - margin)
  );
  nav.style.setProperty("--workflow-drag-left", `${clampedLeft}px`);
  nav.style.setProperty("--workflow-drag-top", `${clampedTop}px`);
  nav.classList.add("is-positioned");
}

if (draggableWorkflowNavigation) {
  let savedPosition = null;
  try {
    savedPosition = JSON.parse(localStorage.getItem(workflowNavPositionKey) || "null");
  } catch (_) {
    // A malformed or unavailable saved position should leave the default layout intact.
  }
  if (Number.isFinite(savedPosition?.left) && Number.isFinite(savedPosition?.top)) {
    clampWorkflowNavPosition(savedPosition.left, savedPosition.top);
  }

  let drag = null;
  let suppressClick = false;
  draggableWorkflowNavigation.addEventListener("pointerdown", (event) => {
    if (event.button !== 0 || event.target.closest("a, input, textarea, select")) return;
    const rect = draggableWorkflowNavigation.getBoundingClientRect();
    drag = {
      pointerId: event.pointerId,
      startX: event.clientX,
      startY: event.clientY,
      left: rect.left,
      top: rect.top,
      moved: false
    };
  });

  window.addEventListener("pointermove", (event) => {
    if (!drag || event.pointerId !== drag.pointerId) return;
    const dx = event.clientX - drag.startX;
    const dy = event.clientY - drag.startY;
    if (!drag.moved && Math.hypot(dx, dy) < 5) return;
    drag.moved = true;
    suppressClick = true;
    draggableWorkflowNavigation.classList.add("is-dragging");
    clampWorkflowNavPosition(drag.left + dx, drag.top + dy);
    event.preventDefault();
  }, { passive: false });

  const finishDrag = (event) => {
    if (!drag || event.pointerId !== drag.pointerId) return;
    if (drag.moved) {
      const rect = draggableWorkflowNavigation.getBoundingClientRect();
      try {
        localStorage.setItem(workflowNavPositionKey, JSON.stringify({ left: rect.left, top: rect.top }));
      } catch (_) {
        // Navigation remains movable when browser storage is unavailable.
      }
      window.setTimeout(() => { suppressClick = false; }, 0);
    }
    draggableWorkflowNavigation.classList.remove("is-dragging");
    drag = null;
  };
  window.addEventListener("pointerup", finishDrag);
  window.addEventListener("pointercancel", finishDrag);
  draggableWorkflowNavigation.addEventListener("click", (event) => {
    if (!suppressClick) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    suppressClick = false;
  }, true);
  window.addEventListener("resize", () => {
    if (!draggableWorkflowNavigation.classList.contains("is-positioned")) return;
    const rect = draggableWorkflowNavigation.getBoundingClientRect();
    clampWorkflowNavPosition(rect.left, rect.top);
  });
}

function setOutreachProcessTab(
  tabName
) {
  const validTabs = new Set([
    "connect",
    "acceptance",
    "recipients",
    "messages"
  ]);

  const requested =
    String(
      tabName || "connect"
    ).trim();

  const cleaned =
    validTabs.has(requested)
      ? requested
      : "connect";

  state.outreachProcessTab =
    cleaned;

  if (cleaned !== "acceptance") {
    setAcceptanceWeekMenuOpen(false);
  }

  const outreachVisible = !document.querySelector("#tab-outreach")?.hidden;
  if (outreachVisible) {
    const headings = {
      connect: ["Connect", "Send connection requests to LinkedIn profiles."],
      acceptance: ["Acceptance", "Check which connections were accepted."],
      recipients: ["Recipients", "Prepare the people you want to message."],
      messages: ["Messages", "Create and follow up on your messages."]
    };
    if (els.pageTitle) els.pageTitle.textContent = headings[cleaned][0];
    if (els.pageSubtitle) els.pageSubtitle.textContent = headings[cleaned][1];
  }

  document
    .querySelectorAll(
      "[data-outreach-process-tab]"
    )
    .forEach((button) => {
      const active =
        button.dataset.outreachProcessTab ===
        cleaned;

      if (button.classList.contains("outreach-workflow-tab")) {
        button.classList.toggle("is-active", active && outreachVisible);
        if (active && outreachVisible) button.setAttribute("aria-current", "page");
        else button.removeAttribute("aria-current");
      } else if (button.dataset.tab === "outreach") {
        button.classList.toggle("is-active", active && outreachVisible);
        if (active && outreachVisible) {
          button.setAttribute("aria-current", "page");
        } else {
          button.removeAttribute("aria-current");
        }
      }
    });

  document
    .querySelectorAll(
      "[data-outreach-process-panel]"
    )
    .forEach((panel) => {
      const active = panel.dataset.outreachProcessPanel === cleaned;
      panel.hidden = !active;
      panel.classList.toggle("is-active", active);
    });

  const mainScroll = document.querySelector("#appMainScroll");
  if (mainScroll) {
    mainScroll.scrollTop = 0;
    mainScroll.classList.toggle(
      "is-connect-workspace",
      outreachVisible && cleaned === "connect"
    );
  }

  requestAnimationFrame(syncOutreachWorkflowPill);

  if (cleaned === "recipients") {
    void Promise.all([
      loadOutreachAcceptedPool(),
      loadMessagePreparation()
    ]).then(() => renderOutreachAcceptedPool());
  }

  if (cleaned === "messages") {
    void Promise.all([
      loadMessagePreparation(),
      loadMessageBatches()
    ]);
  }
}



// =========================================================
// SETTINGS
// =========================================================

const SETTINGS_STORAGE_KEY = "linkedinOps.settings.v1";
const LAST_TAB_STORAGE_KEY = "linkedinOps.lastTab";

const DEFAULT_UI_SETTINGS = {
  rememberLastSection: true,
  reduceMotion: false
};

function loadUiSettings() {
  try {
    const saved = JSON.parse(
      localStorage.getItem(SETTINGS_STORAGE_KEY) || "{}"
    );

    return {
      ...DEFAULT_UI_SETTINGS,
      ...(saved && typeof saved === "object" ? saved : {})
    };
  } catch (error) {
    return { ...DEFAULT_UI_SETTINGS };
  }
}

function saveUiSettings(settings) {
  localStorage.setItem(
    SETTINGS_STORAGE_KEY,
    JSON.stringify(settings)
  );
}

function applyUiSettings(settings) {
  document.body.classList.toggle(
    "reduce-motion",
    Boolean(settings.reduceMotion)
  );

  if (els.settingsRememberTab) {
    els.settingsRememberTab.checked =
      Boolean(settings.rememberLastSection);
  }

  if (els.settingsReduceMotion) {
    els.settingsReduceMotion.checked =
      Boolean(settings.reduceMotion);
  }
}

function updateUiSettingsFromControls() {
  const settings = {
    rememberLastSection: Boolean(
      els.settingsRememberTab?.checked
    ),
    reduceMotion: Boolean(
      els.settingsReduceMotion?.checked
    )
  };

  saveUiSettings(settings);
  applyUiSettings(settings);

  if (!settings.rememberLastSection) {
    localStorage.removeItem(
      LAST_TAB_STORAGE_KEY
    );
  }
}

function openSettingsModal() {
  if (!els.settingsModal) {
    return;
  }

  applyUiSettings(loadUiSettings());

  els.settingsModal.hidden = false;
  document.body.classList.add("has-modal-open");
}

function closeSettingsModal() {
  if (!els.settingsModal) {
    return;
  }

  els.settingsModal.hidden = true;
  document.body.classList.remove("has-modal-open");
}

els.settingsButton?.addEventListener(
  "click",
  openSettingsModal
);

els.settingsCloseButton?.addEventListener(
  "click",
  closeSettingsModal
);

els.settingsDoneButton?.addEventListener(
  "click",
  closeSettingsModal
);

els.settingsRememberTab?.addEventListener(
  "change",
  updateUiSettingsFromControls
);

els.settingsReduceMotion?.addEventListener(
  "change",
  updateUiSettingsFromControls
);

els.settingsModal
  ?.querySelectorAll("[data-settings-close]")
  .forEach((element) => {
    element.addEventListener(
      "click",
      closeSettingsModal
    );
  });

applyUiSettings(loadUiSettings());


// =========================================================
// OUTREACH LINKEDIN SESSION STATUS POPUP
// Event-driven: no 1.8s polling.
// =========================================================

function getSessionStatusMeta(status) {
  const cleaned = String(status || "unknown").trim().toLowerCase();

  const map = {
    logged_in: { label: "Logged in", className: "is-logged-in" },
    logged_out: { label: "Logged out", className: "is-logged-out" },
    checkpoint: { label: "Checkpoint", className: "is-checkpoint" },
    busy: { label: "In use", className: "is-busy" },
    pending: { label: "Queued", className: "is-pending" },
    checking: { label: "Checking", className: "is-checking" },
    failed: { label: "Check failed", className: "is-failed" },
    never_checked: { label: "Not checked", className: "" },
    unknown: { label: "Unknown", className: "" }
  };

  return map[cleaned] || map.unknown;
}

function formatSessionCheckedAt(value) {
  if (!value) {
    return "Never checked";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Never checked";
  }

  return date.toLocaleString();
}

function renderSessionStatuses() {
  const accounts = Array.isArray(state.sessionStatuses)
    ? state.sessionStatuses
    : [];

  if (!els.sessionStatusList) {
    return;
  }

  if (!accounts.length) {
    els.sessionStatusList.innerHTML = `
      <div class="session-status-empty">
        No Outreach account session data yet.
      </div>
    `;
  } else {
    els.sessionStatusList.innerHTML = accounts
      .map((account) => {
        const meta = getSessionStatusMeta(account.status);
        const accountId = escapeHtml(account.account_id || "—");
        const displayName = escapeHtml(account.display_name || accountId);
        const checkedAt = formatSessionCheckedAt(account.checked_at);
        const detail = String(account.last_error || "").trim();
        const secondary = detail
          ? `${checkedAt} · ${detail}`
          : checkedAt;

        return `
          <div class="session-status-item">
            <div class="session-status-account">
              <strong>${displayName}</strong>
              <span title="${escapeHtml(secondary)}">
                ${accountId} · ${escapeHtml(secondary)}
              </span>
            </div>
            <span class="session-status-pill ${meta.className}">
              ${escapeHtml(meta.label)}
            </span>
          </div>
        `;
      })
      .join("");
  }

  const loggedInCount = accounts.filter(
    (account) => account.status === "logged_in"
  ).length;

  const attentionCount = accounts.filter(
    (account) => [
      "logged_out",
      "checkpoint",
      "failed"
    ].includes(account.status)
  ).length;

  const activeCheckCount = accounts.filter(
    (account) => ["pending", "checking"].includes(account.status)
  ).length;

  if (els.sessionStatusSummary) {
    if (!accounts.length) {
      els.sessionStatusSummary.textContent = "Not checked yet";
    } else if (activeCheckCount > 0) {
      els.sessionStatusSummary.textContent =
        `${activeCheckCount} checking · ${loggedInCount}/${accounts.length} logged in`;
    } else {
      els.sessionStatusSummary.textContent =
        `${loggedInCount}/${accounts.length} logged in`;
    }
  }

  if (els.sessionStatusBadge) {
    els.sessionStatusBadge.classList.remove(
      "is-healthy",
      "is-warning",
      "is-error"
    );

    if (!accounts.length) {
      els.sessionStatusBadge.textContent = "—";
    } else if (attentionCount > 0) {
      els.sessionStatusBadge.textContent = String(attentionCount);
      els.sessionStatusBadge.classList.add("is-error");
    } else if (activeCheckCount > 0) {
      els.sessionStatusBadge.textContent = "…";
      els.sessionStatusBadge.classList.add("is-warning");
    } else if (loggedInCount === accounts.length) {
      els.sessionStatusBadge.textContent = "OK";
      els.sessionStatusBadge.classList.add("is-healthy");
    } else {
      els.sessionStatusBadge.textContent = String(loggedInCount);
      els.sessionStatusBadge.classList.add("is-warning");
    }
  }

  if (els.sessionStatusCheckButton) {
    els.sessionStatusCheckButton.disabled =
      state.sessionStatusLoading || activeCheckCount > 0;

    els.sessionStatusCheckButton.textContent =
      activeCheckCount > 0
        ? "Checking…"
        : "Check all accounts";
  }

}

function getSessionRealtimeRow(payload) {
  if (!payload || typeof payload !== "object") {
    return null;
  }

  const candidates = [
    payload.new,
    payload.record,
    payload.data?.record,
    payload.data?.new
  ];

  for (const candidate of candidates) {
    if (
      candidate &&
      typeof candidate === "object" &&
      candidate.account_id
    ) {
      return candidate;
    }
  }

  return null;
}

function applySessionRealtimeRow(row) {
  const accountId = String(row?.account_id || "").trim();

  if (!accountId) {
    return;
  }

  const accounts = Array.isArray(state.sessionStatuses)
    ? [...state.sessionStatuses]
    : [];

  const index = accounts.findIndex(
    (account) => String(account.account_id || "") === accountId
  );

  if (index >= 0) {
    accounts[index] = {
      ...accounts[index],
      ...row
    };
  } else {
    accounts.push(row);
  }

  state.sessionStatuses = accounts;
  renderSessionStatuses();
}

function setupSessionStatusRealtime() {
  stopSessionStatusRealtime();

  state.sessionStatusRealtimeReady = false;

  state.sessionStatusRealtimeChannel = client
    .channel("outreach-session-status-modal")
    .on(
      "postgres_changes",
      {
        event: "*",
        schema: "public",
        table: "outreach_account_sessions"
      },
      (payload) => {
        const row = getSessionRealtimeRow(payload);

        if (row) {
          applySessionRealtimeRow(row);
        }
      }
    )
    .subscribe((status) => {
      state.sessionStatusRealtimeReady = status === "SUBSCRIBED";

      if (status === "CHANNEL_ERROR") {
        console.warn(
          "LinkedIn session Realtime channel error. " +
          "Use Check all accounts again after reconnecting."
        );
      }
    });
}

function stopSessionStatusRealtime() {
  if (state.sessionStatusRealtimeChannel) {
    client.removeChannel(
      state.sessionStatusRealtimeChannel
    );

    state.sessionStatusRealtimeChannel = null;
  }

  state.sessionStatusRealtimeReady = false;
}

async function loadSessionStatuses() {
  state.sessionStatusLoading = true;
  renderSessionStatuses();

  try {
    const response = await fetch(
      "/api/outreach/sessions",
      {
        method: "GET",
        headers: { "Accept": "application/json" },
        cache: "no-store"
      }
    );

    const result = await response.json();

    if (!response.ok || !result.ok) {
      throw new Error(
        result.detail || result.error || "Could not load LinkedIn session status."
      );
    }

    state.sessionStatuses = Array.isArray(result.accounts)
      ? result.accounts
      : [];

    if (els.sessionStatusError) {
      els.sessionStatusError.hidden = true;
      els.sessionStatusError.textContent = "";
    }
  } catch (error) {
    if (els.sessionStatusError) {
      els.sessionStatusError.textContent = error.message || String(error);
      els.sessionStatusError.hidden = false;
    }
  } finally {
    state.sessionStatusLoading = false;
    renderSessionStatuses();
  }
}

async function queueSessionStatusCheck() {
  state.sessionStatusLoading = true;
  renderSessionStatuses();

  try {
    const response = await fetch(
      "/api/outreach/sessions/check",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify({})
      }
    );

    const result = await response.json();

    if (!response.ok || !result.ok) {
      throw new Error(
        result.detail || result.error || "Could not queue LinkedIn session checks."
      );
    }

    state.sessionStatuses = Array.isArray(result.accounts)
      ? result.accounts
      : state.sessionStatuses;

    if (els.sessionStatusError) {
      els.sessionStatusError.hidden = true;
      els.sessionStatusError.textContent = "";
    }
  } catch (error) {
    if (els.sessionStatusError) {
      els.sessionStatusError.textContent = error.message || String(error);
      els.sessionStatusError.hidden = false;
    }
  } finally {
    state.sessionStatusLoading = false;
    renderSessionStatuses();
  }
}

function openSessionStatusModal() {
  if (!els.sessionStatusModal) {
    return;
  }

  els.sessionStatusModal.hidden = false;
  document.body.classList.add("has-modal-open");

  // Subscribe only while the popup is open.
  // No timer and no repeated GET requests.
  setupSessionStatusRealtime();
  void loadSessionStatuses();
}

function closeSessionStatusModal() {
  if (!els.sessionStatusModal) {
    return;
  }

  els.sessionStatusModal.hidden = true;
  document.body.classList.remove("has-modal-open");
  stopSessionStatusRealtime();
}


els.sessionStatusButton?.addEventListener(
  "click",
  openSessionStatusModal
);

els.sessionStatusCloseButton?.addEventListener(
  "click",
  closeSessionStatusModal
);

els.sessionStatusCheckButton?.addEventListener(
  "click",
  queueSessionStatusCheck
);

els.sessionStatusModal
  ?.querySelectorAll("[data-session-status-close]")
  .forEach((element) => {
    element.addEventListener(
      "click",
      closeSessionStatusModal
    );
  });


els.acceptanceInsightsDrawerButton?.addEventListener(
  "click",
  openAcceptanceInsightsDrawer
);

els.acceptanceInsightsDrawerClose?.addEventListener(
  "click",
  closeAcceptanceInsightsDrawer
);

els.acceptanceInsightsDrawerBackdrop?.addEventListener(
  "click",
  closeAcceptanceInsightsDrawer
);

els.acceptanceInsightsScopeFilter?.addEventListener(
  "change",
  () => {
    syncAcceptanceInsightsFilters();
    loadAcceptanceInsights();
  }
);

els.acceptanceInsightsJobFilter?.addEventListener(
  "change",
  loadAcceptanceInsights
);

els.acceptanceInsightsWeekFilter?.addEventListener(
  "change",
  loadAcceptanceInsights
);

els.rateLimitDrawerButton?.addEventListener(
  "click",
  openRateLimitDrawer
);

els.rateLimitDrawerClose?.addEventListener(
  "click",
  closeRateLimitDrawer
);

els.rateLimitDrawerBackdrop?.addEventListener(
  "click",
  closeRateLimitDrawer
);

document.addEventListener(
  "keydown",
  (event) => {
    if (event.key !== "Escape") {
      return;
    }

    if (
      els.acceptanceInsightsDrawer?.classList.contains(
        "is-open"
      )
    ) {
      closeAcceptanceInsightsDrawer();
      return;
    }

    if (
      els.rateLimitDrawer?.classList.contains(
        "is-open"
      )
    ) {
      closeRateLimitDrawer();
      return;
    }

    if (
      els.outreachAcceptanceHistoryModal &&
      !els.outreachAcceptanceHistoryModal.hidden
    ) {
      closeAcceptanceHistoryModal();
      return;
    }

    if (
      els.outreachAcceptanceWeekMenu &&
      !els.outreachAcceptanceWeekMenu.hidden
    ) {
      setAcceptanceWeekMenuOpen(false, {restoreFocus: true});
      return;
    }

    if (
      els.outreachAcceptedWeekMenu &&
      !els.outreachAcceptedWeekMenu.hidden
    ) {
      setAcceptedPoolWeekMenuOpen(false, {restoreFocus: true});
      return;
    }

    if (
      els.outreachAcceptedCampaignMenu &&
      !els.outreachAcceptedCampaignMenu.hidden
    ) {
      setAcceptedPoolCampaignMenuOpen(false, {restoreFocus: true});
      return;
    }

    if (
      els.messageBatchWeekMenu &&
      !els.messageBatchWeekMenu.hidden
    ) {
      setMessageBatchWeekMenuOpen(false, {restoreFocus: true});
    }
  }
);


els.refreshButton?.addEventListener(
  "click",
  () => {
    void loadOutreachDashboard();

    const repliesPanel = document.querySelector("#tab-replies");
    if (repliesPanel && !repliesPanel.hidden) {
      void loadOutreachReplies();
    }
    if (!document.querySelector("#tab-campaigns")?.hidden) {
      void loadCampaignPerformance();
    }
  }
);

els.logoutButton?.addEventListener("click", () => {
  const loginScreen = document.querySelector("#loginScreen");
  const workspace = document.querySelector("#loginWorkspace");
  if (!loginScreen || !workspace) return;

  workspace.hidden = true;
  workspace.inert = true;
  loginScreen.hidden = false;
  document.body.classList.add("login-mode");
  window.dispatchEvent(new CustomEvent("linkedin-ops:logout"));
});

els.searchInput?.addEventListener(
  "input",
  applyProfileFilters
);

els.sortSelect?.addEventListener(
  "change",
  applyProfileFilters
);

els.queueSearchInput?.addEventListener(
  "input",
  applyQueueFilters
);

els.queueStatusFilter?.addEventListener(
  "change",
  applyQueueFilters
);

els.youtubeResearchForm?.addEventListener(
  "submit",
  createYoutubeResearchJob
);

els.outreachConnectForm?.addEventListener(
  "submit",
  createOutreachConnectJob
);

els.outreachUrlInput?.addEventListener(
  "input",
  updateOutreachDetectedCount
);
els.outreachCompanyInput?.addEventListener("input", updateOutreachDetectedCount);
for (const [source, target] of [[els.outreachUrlInput, els.outreachCompanyInput], [els.outreachCompanyInput, els.outreachUrlInput]]) {
  source?.addEventListener("scroll", () => {
    if (target && target.scrollTop !== source.scrollTop) target.scrollTop = source.scrollTop;
  });
}
els.outreachCampaignSelect?.addEventListener("change", () => {
  renderConnectCampaignSelection();
  if (els.outreachCampaignSelect.value === NEW_CONNECT_CAMPAIGN) els.outreachNewCampaign?.focus();
});
els.outreachNewCampaign?.addEventListener("input", renderConnectCampaignSelection);
document.querySelector("#outreachReplyCheckButton")?.addEventListener("click", () => {
  void requestOutreachReplyCheck();
});
for (const dropdown of connectDropdowns) setupConnectDropdown(dropdown);
document.addEventListener("click", (event) => {
  for (const dropdown of connectDropdowns) {
    if (!dropdown.trigger?.parentElement?.contains(event.target)) closeConnectDropdown(dropdown);
  }
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    for (const dropdown of connectDropdowns) {
      if (!dropdown.menu?.hidden) closeConnectDropdown(dropdown, true);
    }
  }
});
els.connectHistoryCampaignFilter?.addEventListener("change", () => {
  if (els.connectHistoryDateFilter) els.connectHistoryDateFilter.value = "";
  const jobs = state.outreachRecentJobs.filter((job) => !els.connectHistoryCampaignFilter.value || job.campaign_id === els.connectHistoryCampaignFilter.value);
  state.expandedConnectWeekKey = jobs.length
    ? connectWeekStart(jobs[0].created_at)?.toISOString().slice(0, 10) || "unknown"
    : null;
  renderConnectHistory(state.outreachRecentJobs);
});
els.connectHistoryDateFilter?.addEventListener("change", () => {
  const date = els.connectHistoryDateFilter.value;
  const job = state.outreachRecentJobs.find((item) =>
    (!els.connectHistoryCampaignFilter?.value || item.campaign_id === els.connectHistoryCampaignFilter.value)
    && (!date || connectDayKey(item.created_at) === date));
  state.expandedConnectWeekKey = job
    ? connectWeekStart(job.created_at)?.toISOString().slice(0, 10) || "unknown"
    : null;
  renderConnectHistory(state.outreachRecentJobs);
});


document.addEventListener(
  "click",
  (event) => {
    const messageBatchWeekButton = event.target.closest("[data-message-batch-week-option]");

    if (messageBatchWeekButton) {
      state.messageBatchWeekKey =
        messageBatchWeekButton.dataset.messageBatchWeekOption || null;
      state.messageBatchPage = 1;
      state.messageBatchSourceFilter = "all";
      setMessageBatchWeekMenuOpen(false, {restoreFocus: true});
      renderMessagePreparation();
      return;
    }

    const replyButton = event.target.closest(".outreach-reply-tab");

    if (replyButton) {
      event.preventDefault();
      switchTab("replies");
      void loadOutreachReplies();
      return;
    }

    const button =
      event.target.closest(
        "[data-outreach-process-tab]"
      );

    if (!button) {
      return;
    }

    event.preventDefault();

    if (document.querySelector("#tab-outreach")?.hidden) {
      switchTab("outreach");
    }

    setOutreachProcessTab(
      button.dataset.outreachProcessTab
    );
  }
);
els.outreachHistoryPrevPage?.addEventListener("click",()=>{state.outreachHistoryPage=Math.max(1,state.outreachHistoryPage-1);renderOutreachHistory(state.outreachRecentJobs)});
els.outreachHistoryNextPage?.addEventListener("click",()=>{state.outreachHistoryPage+=1;renderOutreachHistory(state.outreachRecentJobs)});
els.outreachAcceptancePrevPage?.addEventListener("click",()=>{state.outreachAcceptancePage=Math.max(1,state.outreachAcceptancePage-1);renderOutreachAcceptanceJobs(state.outreachRecentJobs)});
els.outreachAcceptanceNextPage?.addEventListener("click",()=>{state.outreachAcceptancePage+=1;renderOutreachAcceptanceJobs(state.outreachRecentJobs)});

els.outreachAcceptanceWeekButton?.addEventListener("click", () => {
  setAcceptanceWeekMenuOpen(els.outreachAcceptanceWeekMenu?.hidden);
});

els.outreachAcceptanceCampaignFilter?.addEventListener("change", () => {
  state.outreachAcceptanceCampaign = els.outreachAcceptanceCampaignFilter.value || "";
  state.outreachAcceptanceWeekKey = null;
  state.outreachAcceptancePage = 1;
  state.outreachAcceptanceSelectedDeleteJobIds.clear();
  renderOutreachAcceptanceJobs(state.outreachRecentJobs);
});

els.outreachAcceptanceWeekButton?.addEventListener("keydown", (event) => {
  if (event.key !== "ArrowDown") return;
  event.preventDefault();
  setAcceptanceWeekMenuOpen(true);
  els.outreachAcceptanceWeekMenu?.querySelector("button")?.focus();
});

document.addEventListener("click", (event) => {
  if (!els.outreachAcceptanceWeekPicker?.contains(event.target)) {
    setAcceptanceWeekMenuOpen(false);
  }
});

els.outreachAcceptanceWeekMenu?.addEventListener("click", (event) => {
  const option = event.target.closest("[data-acceptance-week-option]");

  if (!option) {
    return;
  }

  state.outreachAcceptanceWeekKey = option.dataset.acceptanceWeekOption || null;
  state.outreachAcceptancePage = 1;
  setAcceptanceWeekMenuOpen(false, {restoreFocus: true});
  renderOutreachAcceptanceJobs(state.outreachRecentJobs);
});

els.outreachAcceptedWeekButton?.addEventListener("click", () => {
  setAcceptedPoolWeekMenuOpen(els.outreachAcceptedWeekMenu?.hidden);
});

els.outreachAcceptedWeekButton?.addEventListener("keydown", (event) => {
  if (event.key !== "ArrowDown") return;
  event.preventDefault();
  setAcceptedPoolWeekMenuOpen(true);
  els.outreachAcceptedWeekMenu?.querySelector("button")?.focus();
});

document.addEventListener("click", (event) => {
  if (!els.outreachAcceptedWeekPicker?.contains(event.target)) {
    setAcceptedPoolWeekMenuOpen(false);
  }
});

els.outreachAcceptedCampaignButton?.addEventListener("click", () => {
  setAcceptedPoolCampaignMenuOpen(els.outreachAcceptedCampaignMenu?.hidden);
});

els.outreachAcceptedCampaignButton?.addEventListener("keydown", (event) => {
  if (event.key !== "ArrowDown") return;
  event.preventDefault();
  setAcceptedPoolCampaignMenuOpen(true);
  els.outreachAcceptedCampaignMenu?.querySelector("button")?.focus();
});

document.addEventListener("click", (event) => {
  if (!els.outreachAcceptedCampaignPicker?.contains(event.target)) {
    setAcceptedPoolCampaignMenuOpen(false);
  }
});

els.outreachAcceptedCampaignMenu?.addEventListener("click", (event) => {
  const option = event.target.closest("[data-accepted-campaign-option]");
  if (!option) return;
  state.outreachAcceptedCampaignId = option.dataset.acceptedCampaignOption || "";
  state.outreachAcceptedSelectedProspectIds.clear();
  state.outreachAcceptedPoolPage = 1;
  setAcceptedPoolCampaignMenuOpen(false, {restoreFocus: true});
  renderOutreachAcceptedPool();
});

els.outreachAcceptedWeekMenu?.addEventListener("click", (event) => {
  const option = event.target.closest("[data-accepted-week-option]");

  if (!option) {
    return;
  }

  state.outreachAcceptedPoolWeekKey =
    option.dataset.acceptedWeekOption || null;
  state.outreachAcceptedCampaignId = "";
  state.outreachAcceptedSelectedProspectIds.clear();
  state.outreachAcceptedPoolPage = 1;
  setAcceptedPoolWeekMenuOpen(false, {restoreFocus: true});
  renderOutreachAcceptedPool();
});

els.messageBatchWeekButton?.addEventListener("click", () => {
  setMessageBatchWeekMenuOpen(els.messageBatchWeekMenu?.hidden);
});

els.messageBatchWeekButton?.addEventListener("keydown", (event) => {
  if (event.key !== "ArrowDown") return;
  event.preventDefault();
  setMessageBatchWeekMenuOpen(true);
  els.messageBatchWeekMenu?.querySelector("button")?.focus();
});

document.addEventListener("click", (event) => {
  if (!els.messageBatchWeekPicker?.contains(event.target)) {
    setMessageBatchWeekMenuOpen(false);
  }
});

els.outreachAcceptanceHistoryModalClose?.addEventListener(
  "click",
  closeAcceptanceHistoryModal
);

els.outreachAcceptanceHistoryModalBackdrop?.addEventListener(
  "click",
  closeAcceptanceHistoryModal
);

els.outreachAcceptanceDeleteSelectedButton?.addEventListener(
  "click",
  openAcceptanceDeleteJobsModal
);

els.outreachDeleteJobsCloseButton?.addEventListener(
  "click",
  closeAcceptanceDeleteJobsModal
);

els.outreachDeleteJobsCancelButton?.addEventListener(
  "click",
  closeAcceptanceDeleteJobsModal
);

els.outreachDeleteJobsModal
  ?.querySelectorAll("[data-outreach-delete-jobs-close]")
  .forEach((element) => {
    element.addEventListener(
      "click",
      closeAcceptanceDeleteJobsModal
    );
  });

els.outreachDeleteJobsConfirmButton?.addEventListener(
  "click",
  deleteSelectedAcceptanceJobs
);

els.messageBatchSourceFilter?.addEventListener(
  "change",
  () => {
    state.messageBatchSourceFilter =
      els.messageBatchSourceFilter.value ||
      "all";

    state.messageBatchPage =
      1;

    renderMessagePreparation();
  }
);

els.messageBatchPrevPage?.addEventListener("click",()=>{state.messageBatchPage=Math.max(1,state.messageBatchPage-1);renderMessagePreparation()});
els.messageBatchNextPage?.addEventListener("click",()=>{state.messageBatchPage+=1;renderMessagePreparation()});

document.addEventListener(
  "click",
  (event) => {
    const button =
      event.target.closest(
        "[data-accepted-filter]"
      );

    if (!button) {
      return;
    }

    state.outreachAcceptedPoolFilter =
      button.dataset.acceptedFilter ||
      "all";

    state.outreachAcceptedPoolPage =
      1;

    renderOutreachAcceptedPool();
  }
);

els.outreachAcceptedPrevPage?.addEventListener(
  "click",
  () => {
    state.outreachAcceptedPoolPage =
      Math.max(
        1,
        state.outreachAcceptedPoolPage - 1
      );

    renderOutreachAcceptedPool();
  }
);

els.outreachAcceptedNextPage?.addEventListener(
  "click",
  () => {
    state.outreachAcceptedPoolPage += 1;
    renderOutreachAcceptedPool();
  }
);

els.outreachAcceptedSelectPage?.addEventListener(
  "change",
  () => {
    const pageItems =
      getAcceptedPoolPageData().pageItems;

    const eligibleIds =
      getEligibleMessageProspectIds();

    pageItems.forEach((item) => {
      const prospectId =
        String(item.prospect_id || "").trim();

      if (
        !prospectId ||
        !eligibleIds.has(prospectId)
      ) {
        return;
      }

      if (els.outreachAcceptedSelectPage.checked) {
        state.outreachAcceptedSelectedProspectIds.add(prospectId);
      } else {
        state.outreachAcceptedSelectedProspectIds.delete(prospectId);
      }
    });

    renderOutreachAcceptedPool();
  }
);

els.messagePrepareSelectedButton?.addEventListener(
  "click",
  prepareSelectedMessageRecipients
);

els.messagePrepareAllButton?.addEventListener(
  "click",
  prepareAllMessageRecipients
);

els.messagePrepareConfirmCloseButton?.addEventListener(
  "click",
  closeMessagePrepareConfirmModal
);

els.messagePrepareConfirmCancelButton?.addEventListener(
  "click",
  closeMessagePrepareConfirmModal
);

els.messagePrepareConfirmModal
  ?.querySelectorAll(
    "[data-message-prepare-close]"
  )
  .forEach((element) => {
    element.addEventListener(
      "click",
      closeMessagePrepareConfirmModal
    );
  });

els.messagePrepareConfirmButton?.addEventListener(
  "click",
  confirmMessagePreparation
);

els.youtubeSearchInput?.addEventListener(
  "input",
  renderYoutubeResearch
);

[
  els.youtubeKeywordFilter,
  els.youtubeLocationFilter,
  els.youtubeEmailFilter,
  els.youtubeSubscriberFilter,
  els.youtubeSortSelect
]
  .filter(Boolean)
  .forEach((element) => {
    element.addEventListener(
      "change",
      renderYoutubeResearch
    );
  });

els.closeDrawerButton?.addEventListener(
  "click",
  closeDrawer
);


if (els.messageSendCloseButton) {
  els.messageSendCloseButton.addEventListener(
    "click",
    closeMessageSendModal
  );
}

if (els.messageSendCancelButton) {
  els.messageSendCancelButton.addEventListener(
    "click",
    closeMessageSendModal
  );
}

els.messageTemplateInput?.addEventListener("input", () => {
  setMessageTemplateStatus(
    state.messageTemplateCanSave
      ? "Unsaved changes · Save template or Queue & Send"
      : "This message applies only to this batch"
  );
  refreshMessageTemplateControls();
});

els.messageTemplateSaveButton?.addEventListener("click", () => {
  void saveCurrentCampaignMessageTemplate();
});

if (els.messageSendModal) {
  els.messageSendModal
    .querySelectorAll(
      "[data-message-send-close]"
    )
    .forEach((element) => {
      element.addEventListener(
        "click",
        closeMessageSendModal
      );
    });
}

if (els.messageSendConfirmButton) {
  els.messageSendConfirmButton.addEventListener(
    "click",
    async () => {
      const batchId =
        state.messageSendSelectedBatchId;

      const template =
        els.messageTemplateInput?.value ||
        "";

      try {
        if (els.messageSendError) {
          els.messageSendError.hidden = true;
          els.messageSendError.textContent = "";
        }

        await queueMessageBatchForSending(
          batchId,
          template
        );

      } catch (error) {
        console.error(
          "Queue message batch error:",
          error
        );

        setMessageTemplateStatus("Queue failed · Review message and retry");

        if (els.messageSendError) {
          els.messageSendError.textContent =
            error.message ||
            String(error);

          els.messageSendError.hidden = false;
        }
      }
    }
  );
}

els.drawerBackdrop?.addEventListener(
  "click",
  closeDrawer
);

document.addEventListener(
  "keydown",
  (event) => {
    if (event.key === "Escape") {
      closeDrawer();
      closeSettingsModal();
    }
  }
);

const initialUiSettings = loadUiSettings();

const SIDEBAR_COLLAPSED_STORAGE_KEY = "linkedin-ops.sidebar-collapsed";
const appLayout = document.querySelector(".app-layout");

function setSidebarCollapsed(collapsed, {persist = true} = {}) {
  if (!appLayout) return;

  appLayout.classList.toggle("is-sidebar-collapsed", collapsed);
  els.sidebarCollapseButton?.setAttribute("aria-expanded", String(!collapsed));
  els.sidebarCollapseButton?.setAttribute(
    "aria-label",
    collapsed ? "Expand sidebar" : "Collapse sidebar"
  );
  if (els.sidebarCollapseButton) {
    els.sidebarCollapseButton.title = collapsed ? "Expand sidebar" : "Collapse sidebar";
  }

  if (persist) {
    localStorage.setItem(SIDEBAR_COLLAPSED_STORAGE_KEY, String(collapsed));
  }
}

setSidebarCollapsed(
  localStorage.getItem(SIDEBAR_COLLAPSED_STORAGE_KEY) === "true",
  {persist: false}
);

els.sidebarCollapseButton?.addEventListener("click", () => {
  setSidebarCollapsed(!appLayout?.classList.contains("is-sidebar-collapsed"));
});

function filterSidebarNavigation() {
  const query = (els.sidebarNavSearch?.value || "")
    .trim()
    .toLocaleLowerCase();

  document
    .querySelectorAll(".sidebar-nav-group")
    .forEach((group) => {
      const buttons = [...group.querySelectorAll(".tab-button")];
      let visibleCount = 0;

      buttons.forEach((button) => {
        const matches = !query || button.textContent
          .toLocaleLowerCase()
          .includes(query);

        button.classList.toggle("is-search-hidden", !matches);
        visibleCount += Number(matches);
      });

      group.classList.toggle("is-search-empty", visibleCount === 0);
    });
}

els.sidebarNavSearch?.addEventListener("input", filterSidebarNavigation);

document.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
    event.preventDefault();
    els.sidebarNavSearch?.focus();
    els.sidebarNavSearch?.select();
  }

  if (event.key === "Escape" && document.activeElement === els.sidebarNavSearch) {
    els.sidebarNavSearch.value = "";
    filterSidebarNavigation();
    els.sidebarNavSearch.blur();
  }
});

if (initialUiSettings.rememberLastSection) {
  const savedTab = localStorage.getItem(
    LAST_TAB_STORAGE_KEY
  );

  if (
    savedTab === "outreach" ||
    savedTab === "replies" ||
    savedTab === "campaigns"
  ) {
    switchTab(savedTab);

    if (savedTab === "replies") {
      void loadOutreachReplies();
    }
    if (savedTab === "campaigns") {
      void loadCampaignPerformance();
    }
  }
}

updateOutreachDetectedCount();
renderConnectCampaignSelection();
void loadConnectCampaigns();

renderOutreachDashboard();

renderOutreachSubmittingState();

loadOutreachDashboard();

renderWorkerActivity();
void loadWorkerActivity();
window.setInterval(() => {
  if (!document.hidden) void loadWorkerActivity();
}, 15000);
window.setInterval(() => { void pollOutreachReplyRevision(); }, 30000);
window.setInterval(() => { void pollLatestOutreachReplyScan(); }, 5000);

startOutreachPolling();

// The presentation-only login may load this script after DOMContentLoaded.
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    setOutreachProcessTab(state.outreachProcessTab || "connect");
  }, { once: true });
} else {
  setOutreachProcessTab(state.outreachProcessTab || "connect");
}


document.addEventListener(
  "keydown",
  (event) => {
    if (
      event.key === "Escape" &&
      els.outreachDeleteJobsModal &&
      !els.outreachDeleteJobsModal.hidden
    ) {
      closeAcceptanceDeleteJobsModal();
    }
  }
);
