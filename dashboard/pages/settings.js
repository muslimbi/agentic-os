import { renderPlaceholder } from "../utils.js";
export function render() {
  return renderPlaceholder("Settings", "System configuration is not editable through this scaffold.", ["Validated configuration", "Secret references, never secret values", "Policy-controlled changes"]);
}
