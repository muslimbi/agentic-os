import { renderPlaceholder } from "../utils.js";
export function render() {
  return renderPlaceholder("Scheduler", "Review scheduled jobs and their execution state.", ["Job definitions", "Safe pause and resume", "Execution history"]);
}
