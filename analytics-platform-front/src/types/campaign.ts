export type TargetRow = {
  phone_number: string;
  segment?: string | null;
  region?: string | null;
};

export type UploadResult = {
  status: "success";
  total_parsed: number;
  valid: number;
  invalid_count: number;
  duplicates_removed: number;
  invalid_phones: string[];
  preview: TargetRow[];
  targets: TargetRow[];
};
