module.exports = {
  preset: "jest-expo",
  transform: {
    "^.+\\.tsx?$": "ts-jest",
  },
  testEnvironment: "node",
  setupFilesAfterEnv: ["<rootDir>/jest.setup.js"],
  collectCoverageFrom: [
    "services/**/*.ts",
  ],
};
module.exports = {
  preset: "jest-expo",
  transform: {
    "^.+\\.tsx?$": "ts-jest",
  },
  testEnvironment: "node",
  collectCoverageFrom: [
    "services/**/*.ts",
    "!services/logger.ts" // logger tested indirectly
  ],
};