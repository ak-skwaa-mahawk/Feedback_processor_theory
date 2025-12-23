module.exports = {
  preset: "jest-expo",
  transform: {
    "^.+\\.tsx?$": "ts-jest",
  },
  testEnvironment: "node",
  collectCoverage: true,
  collectCoverageFrom: [
    "services/**/*.ts",
    "hooks/**/*.ts",
    "components/**/*.tsx",
  ],
  coverageThreshold: {
    global: {
      branches: 90,
      functions: 95,
      lines: 95,
      statements: 95,
    },
  },
  coverageReporters: ["text", "lcov", "html"],
};
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