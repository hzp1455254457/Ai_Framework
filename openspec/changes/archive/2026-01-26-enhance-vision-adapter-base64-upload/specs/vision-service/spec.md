## ADDED Requirements

### Requirement: Support Base64 Input for Image Editing
**Description:** The Vision Service (specifically TongYi WanXiang adapter) MUST support Base64 encoded image strings as input for image editing operations, automatically handling the necessary conversion to URL format required by the underlying API.

#### Scenario: Edit Local Image
**Given:** A user selects a local image file on the frontend
**When:** The frontend converts the file to a Base64 string and sends an `edit_image` request to the backend
**Then:** The TongYi WanXiang adapter detects the Base64 format
**And:** The adapter uploads the image to a temporary storage (DashScope/OSS) to obtain a URL
**And:** The adapter calls the WanXiang API with the image URL
**And:** The editing operation completes successfully and returns the result URL

#### Scenario: Edit with Local Mask
**Given:** A user provides a mask image as a local file (Base64)
**When:** The frontend sends an `edit_image` request with `mask` as Base64
**Then:** The adapter uploads the mask image to obtain a URL
**And:** The adapter calls the WanXiang API with the mask URL
**And:** The operation succeeds
